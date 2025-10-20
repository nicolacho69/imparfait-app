// small client-side niceties can be extended later
document.addEventListener('DOMContentLoaded', () => {
  // prevent accidental form resubmission on reload
  if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
  }
});
