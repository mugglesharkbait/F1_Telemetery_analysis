/// <reference types="vite/client" />

/**
 * Type definitions for CSS module imports
 * This allows TypeScript to understand .css file imports
 */
declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

/**
 * Vite environment variables
 * Add your custom env variables here
 */
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  // Add more env variables as needed
  // readonly VITE_APP_TITLE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
