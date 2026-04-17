/**
 * Not Found Page
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Typography, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { isAuthenticated } from '../utils/auth';

const NotFound = () => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    if (isAuthenticated()) {
      navigate('/');
    } else {
      navigate('/login');
    }
  };

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          textAlign: 'center',
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 100, color: 'error.main', mb: 2 }} />

        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom>
          Page Not Found
        </Typography>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          The page you're looking for doesn't exist or has been moved.
        </Typography>

        <Button
          variant="contained"
          size="large"
          onClick={handleGoHome}
        >
          Go to Home
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound;
