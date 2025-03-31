import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  TextField,
  Breadcrumbs,
  Link,
  Divider,
  Card,
  CardContent,
  IconButton,
  Collapse,
  Tabs,
  Tab,
  Button,
} from '@mui/material';
import {
  Book as BookIcon,
  Code as CodeIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  VideoLibrary as VideoIcon,
  School as TutorialIcon,
  Help as HelpIcon,
  GitHub as GitHubIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface DocSection {
  id: string;
  title: string;
  content: string;
  type: 'guide' | 'api' | 'tutorial';
  category: string;
  tags: string[];
  codeExamples?: Array<{
    language: string;
    code: string;
    description: string;
  }>;
  videoUrl?: string;
}

interface DocCategory {
  id: string;
  title: string;
  icon: React.ReactNode;
  sections: DocSection[];
}

const Documentation: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<DocSection | null>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState(0);

  const categories: DocCategory[] = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: <BookIcon />,
      sections: [
        {
          id: 'quick-start',
          title: 'Quick Start Guide',
          content: 'Learn how to set up and start using the platform...',
          type: 'guide',
          category: 'getting-started',
          tags: ['setup', 'installation', 'basics'],
          codeExamples: [
            {
              language: 'bash',
              code: 'git clone https://github.com/org/repo\ncd repo\nnpm install',
              description: 'Clone and install the project',
            },
          ],
        },
        // Add more sections...
      ],
    },
    {
      id: 'features',
      title: 'Features & Capabilities',
      icon: <CodeIcon />,
      sections: [
        {
          id: 'ide-features',
          title: 'IDE Features',
          content: 'Explore the powerful features of our integrated development environment...',
          type: 'guide',
          category: 'features',
          tags: ['ide', 'coding', 'tools'],
          codeExamples: [
            {
              language: 'typescript',
              code: 'function example() {\n  // Smart code completion\n  const value = "example";\n}',
              description: 'Smart code completion example',
            },
          ],
        },
        // Add more sections...
      ],
    },
    // Add more categories...
  ];

  const handleCategoryClick = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setSelectedSection(null);
  };

  const handleSectionClick = (section: DocSection) => {
    setSelectedSection(section);
  };

  const toggleExpanded = (itemId: string) => {
    setExpandedItems((prev) =>
      prev.includes(itemId)
        ? prev.filter((id) => id !== itemId)
        : [...prev, itemId]
    );
  };

  const filteredCategories = categories.map((category) => ({
    ...category,
    sections: category.sections.filter(
      (section) =>
        section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.tags.some((tag) =>
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        )
    ),
  }));

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {/* Left Sidebar - Navigation */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <TextField
              fullWidth
              placeholder="Search documentation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ mb: 2 }}
            />
            <List>
              {filteredCategories.map((category) => (
                <React.Fragment key={category.id}>
                  <ListItem
                    button
                    onClick={() => toggleExpanded(category.id)}
                    selected={selectedCategory === category.id}
                  >
                    <ListItemIcon>{category.icon}</ListItemIcon>
                    <ListItemText primary={category.title} />
                    {expandedItems.includes(category.id) ? (
                      <ExpandMoreIcon />
                    ) : (
                      <ChevronRightIcon />
                    )}
                  </ListItem>
                  <Collapse in={expandedItems.includes(category.id)}>
                    <List disablePadding>
                      {category.sections.map((section) => (
                        <ListItem
                          key={section.id}
                          button
                          onClick={() => handleSectionClick(section)}
                          selected={selectedSection?.id === section.id}
                          sx={{ pl: 4 }}
                        >
                          <ListItemText
                            primary={section.title}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Collapse>
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} md={9}>
          <Paper sx={{ p: 3 }}>
            {selectedSection ? (
              <>
                <Breadcrumbs sx={{ mb: 3 }}>
                  <Link
                    component="button"
                    variant="body2"
                    onClick={() => setSelectedCategory(null)}
                  >
                    Documentation
                  </Link>
                  <Link
                    component="button"
                    variant="body2"
                    onClick={() => setSelectedSection(null)}
                  >
                    {categories.find((c) => c.id === selectedSection.category)?.title}
                  </Link>
                  <Typography color="text.primary">{selectedSection.title}</Typography>
                </Breadcrumbs>

                <Typography variant="h4" gutterBottom>
                  {selectedSection.title}
                </Typography>

                <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                  <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
                    <Tab label="Guide" />
                    <Tab label="Examples" />
                    {selectedSection.videoUrl && <Tab label="Video Tutorial" />}
                  </Tabs>
                </Box>

                {activeTab === 0 && (
                  <Box>
                    <Typography variant="body1" sx={{ mb: 3 }}>
                      {selectedSection.content}
                    </Typography>
                  </Box>
                )}

                {activeTab === 1 && selectedSection.codeExamples && (
                  <Box>
                    {selectedSection.codeExamples.map((example, index) => (
                      <Card key={index} sx={{ mb: 3 }}>
                        <CardContent>
                          <Typography variant="subtitle1" gutterBottom>
                            {example.description}
                          </Typography>
                          <SyntaxHighlighter
                            language={example.language}
                            style={vscDarkPlus}
                          >
                            {example.code}
                          </SyntaxHighlighter>
                          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                            <Button
                              size="small"
                              startIcon={<CodeIcon />}
                              onClick={() => {
                                navigator.clipboard.writeText(example.code);
                              }}
                            >
                              Copy Code
                            </Button>
                            <Button
                              size="small"
                              startIcon={<GitHubIcon />}
                              href="#"
                              target="_blank"
                            >
                              View on GitHub
                            </Button>
                          </Box>
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                )}

                {activeTab === 2 && selectedSection.videoUrl && (
                  <Box>
                    <iframe
                      width="100%"
                      height="480"
                      src={selectedSection.videoUrl}
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </Box>
                )}
              </>
            ) : (
              <Box>
                <Typography variant="h4" gutterBottom>
                  Documentation
                </Typography>
                <Typography variant="body1" paragraph>
                  Welcome to our comprehensive documentation. Choose a category from the
                  left sidebar to get started.
                </Typography>

                <Grid container spacing={3}>
                  {categories.map((category) => (
                    <Grid item xs={12} sm={6} key={category.id}>
                      <Card
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleCategoryClick(category.id)}
                      >
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            {category.icon}
                            <Typography variant="h6" sx={{ ml: 1 }}>
                              {category.title}
                            </Typography>
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {category.sections.length} articles
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Documentation; 