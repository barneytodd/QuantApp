export function getApiUrl() {
  const server = "localhost";
  const port =
    window.RUNTIME_CONFIG?.REACT_APP_BACKEND_PORT ||
    process.env.REACT_APP_BACKEND_PORT ||
    8000;

  return `http://${server}:${port}`;
}