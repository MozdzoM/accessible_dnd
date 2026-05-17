import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { apiRequest, ApiError } from "../api/client";
import type { AuthResponse, User, UserSettings } from "../api/types";

type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  user: User | null;
  accessToken: string | null;
  status: AuthStatus;
  language: "pl" | "en";
  announcement: string;
  login: (payload: { 
    username: string;
    password: string;
  }) => Promise<void>;
  register: (payload: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (nextUser: User) => void;
  announce: (message: string) => void;
  authenticatedRequest: <T>(path: string, init?: RequestInit) => Promise<T>;
}

const defaultSettings: UserSettings = {
  language: "pl",
  theme: "light",
  font_size: "medium",
};

const AuthContext = createContext<AuthContextValue | null>(null);

function applyDocumentPreferences(settings: UserSettings) {
  document.documentElement.lang = settings.language;
  document.documentElement.dataset.theme = settings.theme;
  document.documentElement.dataset.fontSize = settings.font_size;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [announcement, setAnnouncement] = useState("");

  const announce = useCallback((message: string) => {
    setAnnouncement("");
    window.setTimeout(() => setAnnouncement(message), 10);
  }, []);

  const refreshSession = useCallback(async (): Promise<string | null> => {
    try {
      const data = await apiRequest<{ access: string }>("/auth/refresh/", {
        method: "POST",
      });
      setAccessToken(data.access);
      return data.access;
    } catch {
      setAccessToken(null);
      return null;
    }
  }, []);

  const loadCurrentUser = useCallback(async (token: string) => {
    const data = await apiRequest<User>("/me/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    setUser(data);
    applyDocumentPreferences(data.settings);
    setStatus("authenticated");
  }, []);

  useEffect(() => {
    let mounted = true;
    const bootstrap = async () => {
      const token = await refreshSession();
      if (!mounted) {
        return;
      }
      if (!token) {
        setUser(null);
        applyDocumentPreferences(defaultSettings);
        setStatus("anonymous");
        return;
      }
      try {
        await loadCurrentUser(token);
      } catch {
        setUser(null);
        setAccessToken(null);
        applyDocumentPreferences(defaultSettings);
        setStatus("anonymous");
      }
    };
    void bootstrap();
    return () => {
      mounted = false;
    };
  }, [loadCurrentUser, refreshSession]);

  const authenticatedRequest = useCallback(
    async <T,>(path: string, init: RequestInit = {}): Promise<T> => {
      const perform = async (token: string | null) => {
        const headers = new Headers(init.headers);
        if (token) {
          headers.set("Authorization", `Bearer ${token}`);
        }
        return apiRequest<T>(path, { ...init, headers });
      };

      try {
        return await perform(accessToken);
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 401) {
          throw error;
        }
        const refreshed = await refreshSession();
        if (!refreshed) {
          setUser(null);
          setStatus("anonymous");
          announce("Sesja wygasła. Zaloguj się ponownie.");
          throw error;
        }
        return perform(refreshed);
      }
    },
    [accessToken, announce, refreshSession, user?.settings.language]
  );

  const login = useCallback(
    async (payload: { username: string; password: string }) => {
      const response = await apiRequest<AuthResponse>("/auth/login/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setAccessToken(response.access);
      setUser(response.user);
      applyDocumentPreferences(response.user.settings);
      setStatus("authenticated");
    },
    []
  );

  const register = useCallback(
    async (payload: {
      username: string;
      email: string;
      password: string;
      password_confirm: string;
    }) => {
      await apiRequest<User>("/auth/register/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    []
  );

  const logout = useCallback(async () => {
    await apiRequest<void>("/auth/logout/", { method: "POST" });
    setUser(null);
    setAccessToken(null);
    setStatus("anonymous");
    applyDocumentPreferences(defaultSettings);
  }, []);

  const updateUser = useCallback((nextUser: User) => {
    setUser(nextUser);
    applyDocumentPreferences(nextUser.settings);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      status,
      language: user?.settings.language ?? "pl",
      announcement,
      login,
      register,
      logout,
      updateUser,
      announce,
      authenticatedRequest,
    }),
    [accessToken, announcement, authenticatedRequest, announce, login, logout, register, status, updateUser, user]
  );

  return (
    <AuthContext.Provider value={value}>
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

