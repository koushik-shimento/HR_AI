import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { apiPost, clearToken } from '../api.js';
import { useFrontendPolish } from './FrontendPolish.jsx';

function Navbar() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const [colorTheme, setColorTheme] = useState(() => {
    if (localStorage.getItem('color_theme_version') !== 'ember-v1') {
      localStorage.setItem('color_theme_version', 'ember-v1');
      localStorage.setItem('color_theme', 'warm');
      return 'warm';
    }
    return localStorage.getItem('color_theme') || 'warm';
  });
  const polish = useFrontendPolish();

  useEffect(() => {
    document.body.classList.toggle('theme-warm', colorTheme === 'warm');
  }, [colorTheme]);

  const handleLogout = async () => {
    try {
      await apiPost('/api/logout', {});
    } catch {
      // If the API is down, still clear the local session and return to login.
    }
    clearToken();
    navigate('/login');
  };

  const isActive = (path) =>
    location.pathname === path || location.pathname.startsWith(path + '/')
      ? 'nav-link active'
      : 'nav-link';

  const toggleColorTheme = () => {
    const next = colorTheme === 'warm' ? 'classic' : 'warm';
    localStorage.setItem('color_theme', next);
    setColorTheme(next);
  };

  return (
    <nav className="navbar navbar-koyeb navbar-clean">
      <div className="nav-container">
        <Link to="/welcome" className="nav-brand" aria-label="Open welcome page">
          <img src="/ShimentoX-Light-Logo.webp" alt="ShimentoX" className="nav-logo"
            onError={(e) => { e.target.style.display = 'none'; }} />
        </Link>
        <div className="nav-links">
          <Link to="/dashboard" className={isActive('/dashboard')}>
            <i className="fas fa-chart-line"></i><span>Dashboard</span>
          </Link>
          <Link to="/jobs" className={isActive('/jobs')}>
            <i className="fas fa-briefcase"></i><span>Jobs</span>
          </Link>
          <Link to="/analyze" className={isActive('/analyze')}>
            <i className="fas fa-code-compare"></i><span>Analyze</span>
          </Link>
          <Link to="/talent" className={isActive('/talent')}>
            <i className="fas fa-users"></i><span>Talent</span>
          </Link>
          <Link to="/clients" className={isActive('/clients')}>
            <i className="fas fa-building"></i><span>Clients</span>
          </Link>
          <Link to="/vendors" className={isActive('/vendors')}>
            <i className="fas fa-handshake"></i><span>Vendors</span>
          </Link>
          <Link to="/admin/workflow" className={isActive('/admin/workflow')}>
            <i className="fas fa-screwdriver-wrench"></i><span>Workflow</span>
          </Link>
          <Link to="/hiring-pipeline" className={isActive('/hiring-pipeline')}>
            <i className="fas fa-route"></i><span>Pipeline</span>
          </Link>
          <Link to="/insights" className={isActive('/insights')}>
            <i className="fas fa-chart-bar"></i><span>Reports</span>
          </Link>
        </div>
        <div className="nav-user">
          <Link to="/profile" className={isActive('/profile')}>
            <i className="fas fa-user-circle"></i><span>Profile</span>
          </Link>
          <button
            type="button"
            onClick={polish.toggle}
            className="nav-link nav-design-toggle"
            title={polish.enabled ? 'Disable interface polish' : 'Enable interface polish'}
            aria-label={polish.enabled ? 'Disable interface polish' : 'Enable interface polish'}
          >
            <i className={polish.enabled ? 'fas fa-wand-magic-sparkles' : 'fas fa-wand-magic'}></i>
          </button>
          <button
            type="button"
            onClick={toggleColorTheme}
            className="nav-link nav-design-toggle"
            title={colorTheme === 'warm' ? 'Use current blue theme' : 'Use graphite ember theme'}
            aria-label={colorTheme === 'warm' ? 'Use current blue theme' : 'Use graphite ember theme'}
          >
            <i className="fas fa-palette"></i>
          </button>
          <button onClick={handleLogout} className="nav-link logout">
            <i className="fas fa-sign-out-alt"></i><span>Exit</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
