import * as env from "$app/env";
import * as svelte_store from "svelte/store";
import * as socket_io_client from "socket.io-client";

const run_config = (env.dev ? "dev" : "prod");
const app_name = "dark-mode-pdf";

const readonly = {
	app_name: app_name,
	repo: `https://github.com/j9108c/${app_name}`,
	description: "converts PDFs to dark mode",
	gh_sponsors_url: "https://github.com/sponsors/j9108c",
	backend: (run_config == "dev" ? "/backend" : ""),
	socket: socket_io_client.io((run_config == "dev" ? `http://${(env.browser ? location.hostname : "localhost")}:1201` : ""))
};

const writable = svelte_store.writable({ // global state
	other_apps_urls: null
});

export {
	readonly,
	writable
};
