(() => {
  const gate = document.getElementById('auth-gate');
  if (!gate) return;
  let unlocked = false;
  function unlock(user) {
    if (unlocked) return;
    unlocked = true;
    gate.hidden = true;
    document.body.classList.remove('auth-locked');
    window.dispatchEvent(new Event('dsa:authenticated'));
    const header = document.querySelector('.app-header');
    if (header && user?.name) {
      const badge = document.createElement('span');
      badge.className = 'auth-username';
      badge.textContent = '♛ ' + user.name;
      header.appendChild(badge);
    }
    if (header && !document.getElementById('auth-logout')) {
      const button = document.createElement('button');
      button.id = 'auth-logout';
      button.type = 'button';
      button.textContent = 'LOG OUT';
      button.style.cssText = 'background:#0b223a;border:1px solid #376387;color:#c9e8ff;border-radius:7px;padding:7px 10px;cursor:pointer;font-size:11px';
      button.addEventListener('click', async () => {
        await fetch('/api/auth/logout', {method:'POST'}).catch(() => {});
        window.location.assign('/');
      });
      header.appendChild(button);
    }
  }
  async function checkSession() {
    try {
      const res = await fetch('/api/auth/me', {credentials:'same-origin', cache:'no-store'});
      const data = await res.json();
      if (data.authenticated) unlock(data.user);
    } catch (error) { /* Keep login visible if the server is unavailable. */ }
  }
  window.addEventListener('message', event => {
    if (event.origin !== window.location.origin || event.source !== document.getElementById('cosmic-login-frame')?.contentWindow) return;
    if (event.data?.type === 'dsa-auth-success') checkSession();
  });
  checkSession();
  // If Google OAuth redirects back with an error, make the failure visible in the login iframe.
  const oauthError = new URLSearchParams(window.location.search).get('auth_error');
  if (oauthError) {
    const frame = document.getElementById('cosmic-login-frame');
    if (frame) frame.addEventListener('load', () => {
      try {
        const message = frame.contentDocument?.getElementById('message');
        if (message) {
          message.textContent = oauthError;
          message.style.cssText = 'display:block;color:#ffcad1!important;font-size:13px;font-weight:700;line-height:1.5;padding:10px 12px;border:1px solid #a8495a;background:#431827;border-radius:7px;margin-top:12px';
        }
      } catch(e) {}
    });
  }
})();
