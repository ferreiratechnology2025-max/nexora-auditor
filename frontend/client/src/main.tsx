import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { PerformanceOptimizer } from "@/lib/audit-cache";

// Ativar otimizações de performance
PerformanceOptimizer.setupLazyLoading();
PerformanceOptimizer.reportWebVitals((metrics) => {
    console.log("Web Vitals:", metrics);
});

createRoot(document.getElementById("root")!).render(<App />);

