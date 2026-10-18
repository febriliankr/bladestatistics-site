// Shared by /login and /account. The session is the API's 24-hour JWT, kept in
// localStorage on this origin only; the desktop app signs in separately.
(function () {
  var API = "https://api.skalatec.com";
  // Local previews can point at a dev API: localStorage["blade.api"].
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) {
    try {
      API = localStorage.getItem("blade.api") || API;
    } catch (e) {}
  }
  var KEY = "blade.session";

  function load() {
    try {
      var s = JSON.parse(localStorage.getItem(KEY) || "null");
      if (s && s.token && s.expires > Date.now()) return s;
    } catch (e) {}
    clear();
    return null;
  }

  function save(auth) {
    var s = {
      token: auth.token,
      email: auth.user && auth.user.email,
      name: auth.user && auth.user.name,
      // The token lasts 24 hours; expire it locally a little early.
      expires: Date.now() + 23 * 60 * 60 * 1000,
    };
    try {
      localStorage.setItem(KEY, JSON.stringify(s));
    } catch (e) {}
    return s;
  }

  function clear() {
    try {
      localStorage.removeItem(KEY);
    } catch (e) {}
  }

  // Resolves to the parsed JSON body; rejects with an Error whose message is
  // safe to show and whose status is the HTTP status (0 for network errors).
  function request(method, path, body, token) {
    var headers = { "Content-Type": "application/json" };
    if (token) headers.Authorization = "Bearer " + token;
    return fetch(API + path, {
      method: method,
      headers: headers,
      body: body ? JSON.stringify(body) : undefined,
    })
      .catch(function () {
        var err = new Error("Network error. Check your connection and try again.");
        err.status = 0;
        throw err;
      })
      .then(function (r) {
        return r
          .json()
          .catch(function () {
            return {};
          })
          .then(function (b) {
            if (r.ok) return b;
            var err = new Error(friendly(r.status, b && b.message));
            err.status = r.status;
            throw err;
          });
      });
  }

  function friendly(status, message) {
    if (status === 429) return "Too many codes requested. Wait a few minutes, then try again.";
    if (status === 401 && message === "invalid or expired code")
      return "That code is incorrect or has expired.";
    if (status >= 500 && status !== 503) return "Something went wrong on our side. Please try again.";
    if (message) return message.charAt(0).toUpperCase() + message.slice(1) + ".";
    return "Something went wrong. Please try again.";
  }

  // Only same-site paths are allowed as a post-login destination.
  function nextPath(fallback) {
    var next = new URLSearchParams(location.search).get("next") || "";
    return /^\/(?!\/)[\w\-./?=&#]*$/.test(next) ? next : fallback;
  }

  window.BladeAuth = {
    load: load,
    save: save,
    clear: clear,
    request: request,
    nextPath: nextPath,
  };
})();
