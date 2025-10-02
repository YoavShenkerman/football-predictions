import React, { useState } from "react";
import axios from "axios";

const PredictionsPage = () => {
    const teams = [
        "Alaves", "Almeria", "Ath Bilbao", "Ath Madrid", "FC Barcelona", "Real Betis",
        "Cadiz", "Elche", "Espanyol", "Getafe", "Girona", "Granada",
        "Las Palmas", "Leganes", "Levante", "Mallorca", "Osasuna",
        "Rayo Vallecano", "Real Madrid", "Real Oviedo", "Real Sociedad",
        "Sevilla", "Valencia", "Valladolid", "Villarreal"
    ];

    const [homeTeam, setHomeTeam] = useState("");
    const [awayTeam, setAwayTeam] = useState("");
    const [matchDate, setMatchDate] = useState("");
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState("");

    const today = new Date().toISOString().split("T")[0];
    const leagueEndDate = "2026-05-31";

    const handlePredict = async () => {
        setError("");
        setPrediction(null);

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

    return (
        <div style={{ padding: "20px" }}>
            <h1>Predictions</h1>

            {/* Home Team */}
            <div style={{ margin: "10px 0" }}>
                <label>Home Team: </label>
                <select value={homeTeam} onChange={e => setHomeTeam(e.target.value)}>
                    <option value="">--Select Home Team--</option>
                    {teams.map((team, index) => (
                        <option key={index} value={team}>{team}</option>
                    ))}
                </select>
            </div>

            {/* Away Team */}
            <div style={{ margin: "10px 0" }}>
                <label>Away Team: </label>
                <select value={awayTeam} onChange={e => setAwayTeam(e.target.value)}>
                    <option value="">--Select Away Team--</option>
                    {teams.map((team, index) => (
                        <option key={index} value={team}>{team}</option>
                    ))}
                </select>
            </div>

            {/* Match Date */}
            <div style={{ margin: "10px 0" }}>
                <label>Match Date: </label>
                <input
                    type="date"
                    value={matchDate}
                    onChange={e => setMatchDate(e.target.value)}
                    min={today}
                    max={leagueEndDate}
                />
            </div>

            {/* Predict Button */}
            <button onClick={handlePredict} style={{ margin: "10px 0" }}>
                Get Prediction
            </button>

            {/* Error Message */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Prediction Result */}
            {prediction && (
                <div style={{ marginTop: "20px" }}>
                    <h2>Prediction:</h2>
                    <p>{prediction}</p>
                </div>
            )}
        </div>
    );
};

export default PredictionsPage;
