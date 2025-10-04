import React, { useState } from "react";
import axios from "axios";
import '../styles/PredictionsPage.css';

const teams = [
    "Alaves", "Ath Bilbao", "Ath Madrid", "FC Barcelona", "Real Betis",
    "Elche", "Espanyol", "Getafe", "Girona", "Levante", "Mallorca",
    "Osasuna", "Rayo Vallecano", "Real Madrid", "Real Oviedo",
    "Real Sociedad", "Sevilla", "Valencia", "Valladolid", "Villarreal"
].sort();

const PredictionsPage = () => {
    const [homeTeam, setHomeTeam] = useState("");
    const [awayTeam, setAwayTeam] = useState("");
    const [matchDate, setMatchDate] = useState("");
    const [prediction, setPrediction] = useState("");
    const [error, setError] = useState("");

    const today = new Date().toISOString().split("T")[0];
    const leagueEndDate = "2026-05-31";

    const handlePredict = async () => {
        setError("");
        setPrediction("");

        if (!homeTeam || !awayTeam || !matchDate) {
            setError("Please select both teams and a match date.");
            return;
        }

        if (homeTeam === awayTeam) {
            setError("Home and Away teams cannot be the same.");
            return;
        }

        try {
            const response = await axios.post("http://127.0.0.1:8000/predict", {
                homeTeam,
                awayTeam,
                date: matchDate
            });

            if (response.data.prediction) {
                setPrediction(response.data.prediction);
            } else {
                setError("Failed to get prediction. Make sure the teams and date are valid.");
            }
        } catch (err) {
            console.error(err);
            setError("Failed to get prediction. Make sure the backend is running.");
        }
    };

    // צבע הכרטיס לפי הטקסט שמוחזר מה-backend
    const getPredictionClass = (pred) => {
        if (!pred) return "prediction-draw";
        if (pred.includes(homeTeam)) return "prediction-home"; // Home Win
        if (pred.includes(awayTeam)) return "prediction-away"; // Away Win
        return "prediction-draw"; // Draw
    }

    return (
        <div className="predictions-container">
            <h1>La Liga Match Predictions ⚽</h1>

            <div className="match-form">
                <div className="input-group">
                    <label>Home Team:</label>
                    <select value={homeTeam} onChange={e => {
                        setHomeTeam(e.target.value);
                        setPrediction("");
                    }}>
                        <option value="">--Select Home Team--</option>
                        {teams.map((team, idx) => (
                            <option key={idx} value={team}>{team}</option>
                        ))}
                    </select>
                </div>

                <div className="input-group">
                    <label>Away Team:</label>
                    <select value={awayTeam} onChange={e => {
                        setAwayTeam(e.target.value);
                        setPrediction("");
                    }}>
                        <option value="">--Select Away Team--</option>
                        {teams.map((team, idx) => (
                            <option key={idx} value={team}>{team}</option>
                        ))}
                    </select>
                </div>

                <div className="input-group">
                    <label>Match Date:</label>
                    <input
                        type="date"
                        value={matchDate}
                        onChange={e => {
                            setMatchDate(e.target.value);
                            setPrediction("");
                        }}
                        min={today}
                        max={leagueEndDate}
                    />
                </div>

                <button className="predict-btn" onClick={handlePredict}>Get Prediction</button>
            </div>

            {error && <p className="error">{error}</p>}

            {prediction && (
                <div className={`prediction-card ${getPredictionClass(prediction)}`}>
                    {prediction}
                </div>
            )}
        </div>
    );
};

export default PredictionsPage;
