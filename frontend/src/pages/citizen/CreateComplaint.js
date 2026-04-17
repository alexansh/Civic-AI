/**
 * Create Complaint Page
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  FormHelperText,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Chip,
  IconButton,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import UploadIcon from '@mui/icons-material/Upload';
import { complaintsAPI, aiAPI } from '../../services/api';
import { toast } from 'react-toastify';

const CreateComplaint = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    complaint_type: 'public',
    category: '',
    subcategory: '',
    location_address: '',
    location_latitude: '',
    location_longitude: '',
    landmark: '',
    severity_level: 3,
    affected_people_count: 1,
    images: [],
  });
  const [errors, setErrors] = useState({});
  const [aiSuggestions, setAiSuggestions] = useState(null);

  const steps = ['Basic Information', 'Location Details', 'Upload Images', 'Review & Submit'];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleAIClassification = async () => {
    if (!formData.description) {
      toast.warning('Please enter a description first');
      return;
    }

    try {
      const response = await aiAPI.classifyText({ description: formData.description });
      setAiSuggestions(response.data);

      // Auto-suggest category if confidence is high
      if (response.data.category.confidence > 0.6) {
        setFormData({
          ...formData,
          category: response.data.category.category,
        });
        toast.success(`AI suggested category: ${response.data.category.category}`);
      }
    } catch (err) {
      console.error('AI classification error:', err);
    }
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 0) {
      if (!formData.title.trim()) newErrors.title = 'Title is required';
      if (!formData.description.trim()) newErrors.description = 'Description is required';
      if (!formData.category) newErrors.category = 'Category is required';
    } else if (step === 1) {
      if (!formData.location_address) newErrors.location_address = 'Address is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(activeStep)) return;

    setLoading(true);
    try {
      const response = await complaintsAPI.create(formData);
      toast.success('Complaint created successfully!');
      navigate(`/citizen/complaint/${response.data.complaint.id}`);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create complaint');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    // In a real app, you'd upload to a server and get URLs back
    // For now, we'll just store the file names
    setFormData({
      ...formData,
      images: [...formData.images, ...files.map(f => f.name)],
    });
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                error={!!errors.title}
                helperText={errors.title || 'Brief title for your complaint'}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Description"
                name="description"
                multiline
                rows={4}
                value={formData.description}
                onChange={handleChange}
                error={!!errors.description}
                helperText={errors.description || 'Detailed description of the issue'}
              />
              <Button
                variant="outlined"
                size="small"
                onClick={handleAIClassification}
                sx={{ mt: 1 }}
              >
                Get AI Suggestions
              </Button>
              {aiSuggestions && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">AI Suggestions:</Typography>
                  <Chip
                    label={`Category: ${aiSuggestions.category.category} (${(aiSuggestions.category.confidence * 100).toFixed(0)}%)`}
                    color="primary"
                    size="small"
                    sx={{ mr: 1, mt: 1 }}
                  />
                  <Chip
                    label={`Priority: ${aiSuggestions.priority.priority}`}
                    color={
                      aiSuggestions.priority.priority === 'critical' ? 'error' :
                      aiSuggestions.priority.priority === 'high' ? 'warning' : 'info'
                    }
                    size="small"
                    sx={{ mr: 1, mt: 1 }}
                  />
                </Box>
              )}
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                required
                fullWidth
                label="Complaint Type"
                name="complaint_type"
                value={formData.complaint_type}
                onChange={handleChange}
              >
                <MenuItem value="public">Public Issue</MenuItem>
                <MenuItem value="personal">Personal Issue</MenuItem>
              </TextField>
              <FormHelperText>
                Public: roads, street lights, etc. Personal: home repairs
              </FormHelperText>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                required
                fullWidth
                label="Category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                error={!!errors.category}
                helperText={errors.category}
              >
                <MenuItem value="pothole">Pothole</MenuItem>
                <MenuItem value="street_light">Street Light</MenuItem>
                <MenuItem value="garbage">Garbage/Sanitation</MenuItem>
                <MenuItem value="water">Water Supply</MenuItem>
                <MenuItem value="electrical">Electrical</MenuItem>
                <MenuItem value="plumbing">Plumbing</MenuItem>
                <MenuItem value="carpentry">Carpentry</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Subcategory (Optional)"
                name="subcategory"
                value={formData.subcategory}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Severity Level (1-5)"
                name="severity_level"
                type="number"
                inputProps={{ min: 1, max: 5 }}
                value={formData.severity_level}
                onChange={handleChange}
              />
              <FormHelperText>1 = Minor, 5 = Critical</FormHelperText>
            </Grid>

            {formData.complaint_type === 'public' && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Estimated Number of People Affected"
                  name="affected_people_count"
                  type="number"
                  inputProps={{ min: 1 }}
                  value={formData.affected_people_count}
                  onChange={handleChange}
                />
              </Grid>
            )}
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Address/Location"
                name="location_address"
                value={formData.location_address}
                onChange={handleChange}
                error={!!errors.location_address}
                helperText={errors.location_address}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Latitude (Optional)"
                name="location_latitude"
                value={formData.location_latitude}
                onChange={handleChange}
                type="number"
              />
              <FormHelperText>Click on map to auto-fill (feature coming soon)</FormHelperText>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Longitude (Optional)"
                name="location_longitude"
                value={formData.location_longitude}
                onChange={handleChange}
                type="number"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Landmark (Optional)"
                name="landmark"
                value={formData.landmark}
                onChange={handleChange}
                helperText="Nearby landmark to help locate the issue"
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Upload Images
            </Typography>
            <Box
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                mb: 2,
              }}
            >
              <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body1" gutterBottom>
                Click to upload images
              </Typography>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleImageUpload}
                style={{ display: 'none' }}
                id="image-upload"
              />
              <label htmlFor="image-upload">
                <Button variant="contained" component="span">
                  Choose Files
                </Button>
              </label>
            </Box>

            {formData.images.length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Uploaded Images:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {formData.images.map((img, idx) => (
                    <Chip
                      key={idx}
                      label={img}
                      onDelete={() => {
                        const newImages = formData.images.filter((_, i) => i !== idx);
                        setFormData({ ...formData, images: newImages });
                      }}
                    />
                  ))}
                </Box>
              </Box>
            )}

            <Alert severity="info" sx={{ mt: 2 }}>
              Images help authorities and vendors understand the issue better.
              Please upload clear photos of the problem.
            </Alert>
          </Box>
        );

      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Your Complaint
            </Typography>

            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Title
              </Typography>
              <Typography variant="body1" gutterBottom>
                {formData.title}
              </Typography>

              <Typography variant="subtitle2" color="text.secondary">
                Description
              </Typography>
              <Typography variant="body1" gutterBottom>
                {formData.description}
              </Typography>

              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Type
                  </Typography>
                  <Typography variant="body1">
                    {formData.complaint_type}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Category
                  </Typography>
                  <Typography variant="body1">
                    {formData.category}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Location
                  </Typography>
                  <Typography variant="body1">
                    {formData.location_address}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Severity
                  </Typography>
                  <Typography variant="body1">
                    {formData.severity_level}/5
                  </Typography>
                </Grid>
              </Grid>
            </Paper>

            <Alert severity="warning">
              Please verify all information before submitting. You can edit the complaint
              only until it's being reviewed.
            </Alert>
          </Box>
        );

      default:
        return <Typography>Unknown step</Typography>;
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/citizen/dashboard')}
        sx={{ mb: 2 }}
      >
        Back to Dashboard
      </Button>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Create New Complaint
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box component="form" onSubmit={(e) => e.preventDefault()}>
          {renderStepContent(activeStep)}

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            {activeStep > 0 && (
              <Button onClick={handleBack} sx={{ mr: 2 }}>
                Back
              </Button>
            )}
            {activeStep < steps.length - 1 ? (
              <Button variant="contained" onClick={handleNext}>
                Next
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Submit Complaint'}
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default CreateComplaint;
