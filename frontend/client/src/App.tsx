import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";
import Dashboard from "./pages/Dashboard";
import Plans from "./pages/Plans";
import PublicAuditReport from "./pages/PublicAuditReport";
import NotificationHistory from "./pages/NotificationHistory";
import HowItWorks from "./pages/HowItWorks";
import Certifications from "./pages/Certifications";
import Testimonials from "./pages/Testimonials";
import Checkout from "./pages/Checkout";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/checkout"} component={Checkout} />
      <Route path={"/login"} component={Login} />
      <Route path={"/register"} component={Register} />
      <Route path={"/forgot-password"} component={ForgotPassword} />
      <Route path={"/reset-password"} component={ResetPassword} />
      <Route path={"/verify-email"} component={VerifyEmail} />
      <Route path={"/planos"} component={Plans} />
      <Route path={"/como-funciona"} component={HowItWorks} />
      <Route path={"/certificacoes"} component={Certifications} />
      <Route path={"/depoimentos"} component={Testimonials} />
      <Route path={"/v/:auditId"} component={PublicAuditReport} />
      <Route path={"/notifications"} component={() => (
        <ProtectedRoute>
          <NotificationHistory />
        </ProtectedRoute>
      )} />
      <Route path={"/dashboard"} component={() => (
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      )} />
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

import CookieBanner from "./components/CookieBanner";

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
      // switchable
      >
        <AuthProvider>
          <NotificationProvider>
            <TooltipProvider>
              <Toaster />
              <CookieBanner />
              <Router />
            </TooltipProvider>
          </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
