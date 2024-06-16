import {extendTheme, ThemeOverride} from '@chakra-ui/react';
import {TextStyles} from "./textStyles.ts";

const themeOverride: ThemeOverride = {
    fonts: {
        // heading: 'Alright Sans, sans-serif',
        // body: 'Alright Sans, sans-serif',
        body: 'General Sans, sans-serif',
    },
    fontSizes: {
        xs: "12px",   // 0.75rem * 16
        sm: "14px",   // 0.875rem * 16
        md: "16px",   // 1rem * 16
        lg: "18px",   // 1.125rem * 16
        xl: "20px",   // 1.25rem * 16
        "2xl": "24px", // 1.5rem * 16
        "3xl": "28px",
        "4xl": "32px",
        "5xl": "36px",
        "6xl": "40px",
        "7xl": "46px",
        "8xl": "52px",
        "9xl": "588px",
    },
    fontWeights: {
        hairline: 100,
        thin: 200,
        light: 300,
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
        extrabold: 800,
        black: 900,
    },
    styles: {
        global: {
            // Apply the font family to all body text
            body: {
                fontFamily: 'body',
            },
        },
    },
    textStyles: TextStyles,
    colors: {
        customBlack: {
            50: '#f2f2f2', // Very light gray (almost white) for subtle borders or shadows
            100: '#d9d9d9', // Lighter gray
            200: '#bfbfbf', // Light gray
            300: '#a6a6a6', // Medium light gray
            400: '#8c8c8c', // True gray
            500: '#737373', // Dark gray
            600: '#595959', // Darker gray
            700: '#404040', // Even darker gray (near black)
            800: '#262626', // Almost black
            900: '#0d0d0d', // Virtually black
        },
    },
};

export const theme = extendTheme(themeOverride);
