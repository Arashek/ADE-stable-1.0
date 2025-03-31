import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  TextField,
  Tooltip,
} from '@mui/material';
import {
  Description,
  Code,
  Build,
  Search,
  Bookmark,
  Share,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { DocumentationService } from '../../services/DocumentationService';
import { Documentation, DocType } from '../../types/documentation';
import { APIReference } from './APIReference';
import { UserGuide } from './UserGuide';
import { TechnicalDocs } from './TechnicalDocs';
import { MonitoringService } from '../../services/monitoring.service';

const StyledPaper = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'row',
  overflow: 'hidden',
}));

const Sidebar = styled(Box)(({ theme }) => ({
  width: 280,
  borderRight: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  flexDirection: 'column',
}));

const Content = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}));

const SearchBox = styled(TextField)(({ theme }) => ({
  margin: theme.spacing(2),
}));

export const DocumentationBrowser: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<Documentation | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [bookmarks, setBookmarks] = useState<string[]>([]);
  const [recentDocs, setRecentDocs] = useState<Documentation[]>([]);

  const docService = DocumentationService.getInstance();
  const monitoring = MonitoringService.getInstance();

  useEffect(() => {
    loadInitialDocumentation();
  }, []);

  const loadInitialDocumentation = async () => {
    try {
      const startTime = performance.now();
      
      // Load documentation based on active tab
      const docType = getDocTypeFromTab(activeTab);
      const doc = await docService.generateDocumentation('main', docType);
      setSelectedDoc(doc);

      // Record performance metric
      const duration = performance.now() - startTime;
      monitoring.recordMetric({
        category: 'documentation',
        name: 'load_time',
        value: duration,
        tags: { type: docType }
      });
    } catch (error) {
      monitoring.recordError('load_documentation_failed', error);
      // Handle error
    }
  };

  const getDocTypeFromTab = (tab: number): DocType => {
    switch (tab) {
      case 0:
        return DocType.USER_GUIDE;
      case 1:
        return DocType.API;
      case 2:
        return DocType.TECHNICAL;
      default:
        return DocType.USER_GUIDE;
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    loadInitialDocumentation();
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    // Implement search logic
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const toggleBookmark = (docId: string) => {
    setBookmarks(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const addToRecent = (doc: Documentation) => {
    setRecentDocs(prev => {
      const filtered = prev.filter(d => d.id !== doc.id);
      return [doc, ...filtered].slice(0, 10);
    });
  };

  const renderContent = () => {
    if (!selectedDoc) return null;

    switch (activeTab) {
      case 0:
        return <UserGuide doc={selectedDoc} />;
      case 1:
        return <APIReference doc={selectedDoc} />;
      case 2:
        return <TechnicalDocs doc={selectedDoc} />;
      default:
        return null;
    }
  };

  return (
    <StyledPaper elevation={3}>
      <Sidebar>
        <SearchBox
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Search documentation..."
          value={searchQuery}
          onChange={handleSearch}
          InputProps={{
            startAdornment: <Search color="action" />,
          }}
        />
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab icon={<Description />} label="Guide" />
          <Tab icon={<Code />} label="API" />
          <Tab icon={<Build />} label="Technical" />
        </Tabs>
        <Divider />
        <List sx={{ flexGrow: 1, overflow: 'auto' }}>
          {selectedDoc?.sections?.map(section => (
            <React.Fragment key={section.id}>
              <ListItem
                button
                onClick={() => toggleSection(section.id)}
              >
                <ListItemIcon>
                  {expandedSections.includes(section.id) ? (
                    <ExpandLess />
                  ) : (
                    <ExpandMore />
                  )}
                </ListItemIcon>
                <ListItemText primary={section.title} />
                <Tooltip title="Bookmark">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleBookmark(section.id);
                    }}
                  >
                    <Bookmark
                      color={bookmarks.includes(section.id) ? 'primary' : 'action'}
                    />
                  </IconButton>
                </Tooltip>
              </ListItem>
              {expandedSections.includes(section.id) && section.subsections?.map(sub => (
                <ListItem
                  key={sub.id}
                  button
                  sx={{ pl: 4 }}
                >
                  <ListItemText primary={sub.title} />
                </ListItem>
              ))}
            </React.Fragment>
          ))}
        </List>
      </Sidebar>
      <Content>
        {renderContent()}
      </Content>
    </StyledPaper>
  );
};
