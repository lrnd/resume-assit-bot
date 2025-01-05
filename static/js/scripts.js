async function askQuestion() {
    const query = document.getElementById("query").value.trim();
    const responseDiv = document.getElementById("response");
    const loadingDiv = document.getElementById("loading");

    if (!query) {
        alert("Please enter a question.");
        return;
    }

    responseDiv.style.display = "none";
    responseDiv.innerHTML = "";
    loadingDiv.style.display = "block";

    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        loadingDiv.style.display = "none";
        if (data.response) {
            responseDiv.style.display = "block";
            responseDiv.innerHTML = `<strong>Answer:</strong> ${data.response}`;
        } else if (data.error) {
            responseDiv.style.display = "block";
            responseDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
        }
    } catch (error) {
        loadingDiv.style.display = "none";
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
}
// Function to load modals dynamically
async function loadModals() {
    const modalContainer = document.getElementById('modalContainer');
    const modalFiles = ['/templates/help-modal.html'];

    for (const file of modalFiles) {
        const response = await fetch(file);
        const modalHtml = await response.text();
        modalContainer.innerHTML += modalHtml;
    }
}
// Call the function to load modals
document.addEventListener('DOMContentLoaded', loadModals);

function downloadResume() {
    window.open("/static/resume.pdf", "_blank");
}

function reportBug() {
    const bugReportUrl = "https://example.com/report-bug"; // Replace with actual URL
    window.open(bugReportUrl, "_blank");
}

function contactMe() {
    const contactUrl = "mailto:seanphilliptaylor@gmail.com?subject=Contact%20from%20Resume%20Q&A%20Chatbot"; // Replace with actual email
    window.open(contactUrl, "_self");
}

async function submitBugReport(event) {
    event.preventDefault(); // Prevent default form submission behavior

    const description = document.getElementById("bugDescription").value.trim();
    if (!description) {
        alert("Please provide a description of the bug.");
        return;
    }

    try {
        const response = await fetch("/report-bug", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ description })
        });

        if (response.ok) {
            alert("Bug report submitted successfully. Thank you!");
        } else {
            alert("Failed to submit the bug report. Please try again.");
        }
    } catch (error) {
        console.error("Error submitting bug report:", error);
        alert("An error occurred. Please try again.");
    }

    // Clear the form
    document.getElementById("bugReportForm").reset();
}

