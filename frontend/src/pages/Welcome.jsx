import '../styles/Welcome.css';
import useDeviceType from '../hooks/useDeviceType';

function Welcome() {
    const deviceType = useDeviceType();

    return (
        <div className={`welcome-container ${deviceType}`}>
            <div className={`welcome-content ${deviceType}`}>
                <h1 className="glitch" data-text="Welcome to Hiri">Welcome to Hiri</h1>
                <div className="subtitle">The Future of Smart Devices</div>
                <div className="decorative-line"></div>
            </div>
            <div className="cyber-grid"></div>
        </div>
    );
}

export default Welcome;