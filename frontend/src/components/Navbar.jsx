export default function Navbar({ setCurrentPage }) {
    return (
        <nav style={{ marginBottom: "20px" }}>
            <button onClick={() => setCurrentPage("home")}>Home</button>
            <button onClick={() => setCurrentPage("predictions")}>Predictions</button>
        </nav>
    );
}
