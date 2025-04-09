/**
 * Utility to handle CSRF token management
 */
export function setupCSRF() {
    // Function to get CSRF token on app initialization
    const fetchCSRFToken = async () => {
        try {
            // This is a common Django pattern - make a GET request to a page that includes the CSRF token
            const response = await fetch('/api/csrf/', { credentials: 'include' });
            // The token is set in the cookie by this request
            return true;
        } catch (error) {
            console.error("Failed to fetch CSRF token:", error);
            return false;
        }
    };

    // Call this when the app initializes
    fetchCSRFToken();
}
