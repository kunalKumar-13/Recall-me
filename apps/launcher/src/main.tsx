import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

// No StrictMode: the panel pre-renders while hidden and we want a single
// engine fetch + a single content-fit measure, not dev double-invokes.
ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
