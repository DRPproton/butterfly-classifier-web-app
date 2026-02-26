/**
 * Tailwind CSS Configuration for Butterfly Classifier
 * This file configures custom colors, fonts, and design tokens
 * Color palette inspired by nature/mint green theme
 */

tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#30ac59ff",              // Vibrant green
                "background-light": "#f8fcf9",    // Light background
                "background-dark": "#102216",     // Dark green
                "earthy-brown": "#2d241e",        // Brown for text
                "meadow-green": "#4c9a66",        // Meadow green accent

                // Aliases for templates
                "text-dark": "#2d241e",           // Same as earthy-brown
                "text-muted": "#4c9a66",          // Same as meadow-green
                "soft-green": "#4c9a66",          // Same as meadow-green
                "earth-brown": "#2d241e",         // Legacy alias
                "cream-bg": "#f8fcf9",            // Legacy alias
            },
            fontFamily: {
                "display": ["Space Grotesk", "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.50rem",
                "lg": "0.7rem",
                "xl": "1.2rem",
                "full": "9999px"
            },
        },
    },
}

