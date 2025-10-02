import { useState } from "react";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import PredictionsPage from "./pages/PredictionsPage.jsx";
import "./styles/App.css";

function App() {
    const [currentPage, setCurrentPage] = useState("home");

    const renderPage = () => {
        switch (currentPage) {
            case "home":
                return <HomePage />;
            case "predictions":
                return <PredictionsPage />;
            default:
                return <HomePage />;
        }
    };

    return (
        <>
            <Navbar setCurrentPage={setCurrentPage} />
            <main>{renderPage()}</main>
        </>
    );
}

export default App;
