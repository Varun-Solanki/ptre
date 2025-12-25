import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Activity } from 'lucide-react';
import styles from './Layout.module.css';
import clsx from 'clsx';

const Layout = () => {
    const location = useLocation();

    return (
        <div className={styles.appContainer}>
            <nav className={styles.navbar}>
                <div className={styles.navContent}>
                    <Link to="/" className={styles.logo}>
                        <Activity className={styles.logoIcon} />
                        <span className={styles.logoText}>PTRE</span>
                    </Link>

                    <div className={styles.navLinks}>
                        <Link
                            to="/"
                            className={clsx(styles.navLink, location.pathname === '/' && styles.activeLink)}
                        >
                            Intro
                        </Link>
                        <Link
                            to="/dashboard"
                            className={clsx(styles.navLink, location.pathname === '/dashboard' && styles.activeLink)}
                        >
                            Dashboard
                        </Link>
                        <Link
                            to="/features"
                            className={clsx(styles.navLink, location.pathname === '/features' && styles.activeLink)}
                        >
                            Features
                        </Link>
                        <Link
                            to="/labels"
                            className={clsx(styles.navLink, location.pathname === '/labels' && styles.activeLink)}
                        >
                            Labels
                        </Link>
                        <Link
                            to="/system"
                            className={clsx(styles.navLink, location.pathname === '/system' && styles.activeLink)}
                        >
                            System
                        </Link>
                        <Link
                            to="/explanation"
                            className={clsx(styles.navLink, location.pathname === '/explanation' && styles.activeLink)}
                        >
                            Explanation
                        </Link>
                    </div>
                </div>
            </nav>

            <main className={styles.mainContent}>
                <Outlet />
            </main>

            <footer className={styles.footer}>
                PTRE v1.0 • Probabilistic Trend & Risk Engine
            </footer>
        </div>
    );
};

export default Layout;
