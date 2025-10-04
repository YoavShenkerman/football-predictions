export default function Navbar({ setCurrentPage, currentPage }) {
    return (
        <nav
            style={{
                position: "fixed",
                top: "20%",
                right: "1rem",
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem",
                zIndex: 1000,
            }}
        >
            {["home", "predictions"].map((page) => (
                <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    style={{
                        padding: "0.4rem 0.8rem",
                        fontSize: "0.9rem",
                        cursor: "pointer",
                        borderRadius: "5px",
                        border: "1px solid #444",
                        backgroundColor: currentPage === page ? "#444" : "#f0f0f0",
                        color: currentPage === page ? "#fff" : "#000",
                        transition: "all 0.2s",
                    }}
                    onMouseOver={(e) => {
                        if (currentPage !== page) e.currentTarget.style.backgroundColor = "#ddd";
                    }}
                    onMouseOut={(e) => {
                        if (currentPage !== page) e.currentTarget.style.backgroundColor = "#f0f0f0";
                    }}
                >
                    {page.charAt(0).toUpperCase() + page.slice(1)}
                </button>
            ))}
        </nav>
    );
}
