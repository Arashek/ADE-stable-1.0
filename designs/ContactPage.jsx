import React from 'react';
import { 
  Button, 
  TextField, 
  Box, 
  Typography, 
  Container,
  AppBar,
  Toolbar,
  Card,
  CardContent,
  Grid,
  Link
} from '@mui/material';

const ContactPage = () => {
  const [formData, setFormData] = React.useState({});

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Add your form submission logic here
  };

  return (
    <Container maxWidth="lg">
      <AppBar position="static" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6">Contact Page</Typography>
        </Toolbar>
      </AppBar>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>Contact Form</Typography>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Name"
                  name="name"
                  fullWidth
                  required=True
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Email"
                  name="email"
                  fullWidth
                  required=True
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Message"
                  name="message"
                  multiline
                  rows=4
                  fullWidth
                  required=False
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <Button type="submit" variant="contained" color="primary">
                  Submit
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
      <Box component="footer" sx={{ mt: 4, py: 3, borderTop: '1px solid #eaeaea' }}>
        <Grid container justifyContent="space-between">
          <Grid item>
            <Typography variant="body2"> 2025 Contact Page</Typography>
          </Grid>
          <Grid item>
            <Link href="#" sx={ mx: 1 }>Home</Link>
            <Link href="#" sx={ mx: 1 }>About</Link>
            <Link href="#" sx={ mx: 1 }>Contact</Link>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ContactPage;
