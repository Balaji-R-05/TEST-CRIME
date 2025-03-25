// import React, { useState } from 'react';
// import { useNavigate, useLocation } from 'react-router-dom';
// import { useAuth } from '../context/AuthContext';
// import './Login.css';

// const Login = () => {
//   const [username, setUsername] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const navigate = useNavigate();
//   const location = useLocation();
//   const { login } = useAuth();

//   const from = location.state?.from?.pathname || "/";

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setIsLoading(true);
//     setError('');

//     if (!username || !password) {
//       setError('Username and password are required');
//       setIsLoading(false);
//       return;
//     }

//     console.log('Attempting login with username:', username);

//     try {
//       const result = await login(username, password);
//       console.log('Login result:', result);
      
//       if (result.success) {
//         navigate(from, { replace: true });
//       } else {
//         setError(result.error || 'Login failed. Please check your credentials.');
//       }
//     } catch (error) {
//       console.error('Login error:', error);
//       setError(
//         error.response?.data?.detail || 
//         error.message || 
//         'An unexpected error occurred during login'
//       );
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="login-container">
//       <div className="login-box">
//         <h2>Login to CrimeSpot</h2>
//         {error && <div className="error-message">{error}</div>}
//         <form onSubmit={handleSubmit}>
//           <div className="form-group">
//             <label htmlFor="username">Username:</label>
//             <input
//               id="username"
//               type="text"
//               value={username}
//               onChange={(e) => setUsername(e.target.value)}
//               disabled={isLoading}
//               required
//               autoComplete="username"
//             />
//           </div>
//           <div className="form-group">
//             <label htmlFor="password">Password:</label>
//             <input
//               id="password"
//               type="password"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               disabled={isLoading}
//               required
//               autoComplete="current-password"
//             />
//           </div>
//           <button type="submit" disabled={isLoading}>
//             {isLoading ? 'Logging in...' : 'Login'}
//           </button>
//         </form>
//         <div className="login-help">
//           <p>Test Account:</p>
//           <p>Username: admin</p>
//           <p>Password: admin123</p>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Login;




import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';
import axios from 'axios';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const from = location.state?.from?.pathname || "/";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    console.log('Attempting login with username:', username);

    try {
      // First, check if the API is reachable
      const healthCheck = await axios.get('http://127.0.0.1:8000/');
      console.log('API Health Check:', healthCheck.data);

      const result = await login(username, password);
      console.log('Login result:', result);
      
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setError(result.error || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // More detailed error logging
      if (error.response) {
        console.log('Error response data:', error.response.data);
        console.log('Error response status:', error.response.status);
        console.log('Error response headers:', error.response.headers);
        setError(error.response.data?.detail || 'Server responded with an error');
      } else if (error.request) {
        console.log('Error request:', error.request);
        setError('No response received from server. Please check your connection.');
      } else {
        console.log('Error message:', error.message);
        setError(error.message || 'An unexpected error occurred during login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login to CrimeSpot</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
              required
              autoComplete="username"
              className={error && !username.trim() ? "input-error" : ""}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              required
              autoComplete="current-password"
              className={error && !password.trim() ? "input-error" : ""}
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        {process.env.NODE_ENV === 'development' && (
          <div className="login-help">
            <p>Test Account:</p>
            <p>Username: admin</p>
            <p>Password: admin123</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
