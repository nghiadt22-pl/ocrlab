import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { 
  BarChart3, 
  FileText, 
  FolderOpen, 
  Search, 
  Upload, 
  Users, 
  FileUp, 
  FileSearch,
  Clock,
  CreditCard
} from 'lucide-react';
import Header from '@/components/Header';
import { Link } from 'react-router-dom';

// Mock data for usage statistics
const mockUsageData = {
  pagesProcessed: 128,
  documentsUploaded: 24,
  searchQueries: 76,
  storageUsed: '256 MB',
  lastUpload: '2 hours ago'
};

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="flex flex-col gap-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome to OCR Lab. Manage your documents and view usage statistics.
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid grid-cols-3 w-full max-w-md">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="documents">Documents</TabsTrigger>
              <TabsTrigger value="usage">Usage</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      Documents
                    </CardTitle>
                    <CardDescription>Total documents processed</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">{mockUsageData.documentsUploaded}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileUp className="h-5 w-5 text-primary" />
                      Pages
                    </CardTitle>
                    <CardDescription>Total pages processed</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">{mockUsageData.pagesProcessed}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileSearch className="h-5 w-5 text-primary" />
                      Searches
                    </CardTitle>
                    <CardDescription>Total search queries</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">{mockUsageData.searchQueries}</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    <Button variant="outline" className="flex flex-col items-center justify-center h-24 gap-2" asChild>
                      <Link to="/">
                        <Upload className="h-6 w-6" />
                        <span>Upload Document</span>
                      </Link>
                    </Button>
                    <Button variant="outline" className="flex flex-col items-center justify-center h-24 gap-2" asChild>
                      <Link to="/folders">
                        <FolderOpen className="h-6 w-6" />
                        <span>Browse Folders</span>
                      </Link>
                    </Button>
                    <Button variant="outline" className="flex flex-col items-center justify-center h-24 gap-2" asChild>
                      <Link to="/search">
                        <Search className="h-6 w-6" />
                        <span>Search Content</span>
                      </Link>
                    </Button>
                    <Button variant="outline" className="flex flex-col items-center justify-center h-24 gap-2" asChild>
                      <Link to="/dashboard?tab=usage">
                        <BarChart3 className="h-6 w-6" />
                        <span>View Analytics</span>
                      </Link>
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Recent Activity</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="bg-primary/10 p-2 rounded-full">
                        <FileUp className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Document uploaded</p>
                        <p className="text-xs text-muted-foreground">financial_report_2023.pdf</p>
                        <p className="text-xs text-muted-foreground">{mockUsageData.lastUpload}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-primary/10 p-2 rounded-full">
                        <FileSearch className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Search performed</p>
                        <p className="text-xs text-muted-foreground">"quarterly revenue"</p>
                        <p className="text-xs text-muted-foreground">3 hours ago</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="bg-primary/10 p-2 rounded-full">
                        <Clock className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">Processing completed</p>
                        <p className="text-xs text-muted-foreground">meeting_notes.pdf</p>
                        <p className="text-xs text-muted-foreground">5 hours ago</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="documents" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Your Documents</CardTitle>
                  <CardDescription>
                    Manage your uploaded documents and folders
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col items-center justify-center py-8 space-y-4">
                    <p className="text-muted-foreground text-center">
                      Organize your documents into folders for easy access
                    </p>
                    <Button asChild>
                      <Link to="/folders" className="flex items-center gap-2">
                        <FolderOpen className="h-4 w-4" />
                        Manage Folders
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="usage" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Usage Statistics</CardTitle>
                  <CardDescription>
                    Monitor your OCR Lab usage and billing information
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Pages Processed</p>
                        <p className="text-2xl font-bold">{mockUsageData.pagesProcessed}</p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Documents Uploaded</p>
                        <p className="text-2xl font-bold">{mockUsageData.documentsUploaded}</p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Search Queries</p>
                        <p className="text-2xl font-bold">{mockUsageData.searchQueries}</p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Storage Used</p>
                        <p className="text-2xl font-bold">{mockUsageData.storageUsed}</p>
                      </div>
                    </div>

                    <div className="pt-4">
                      <p className="text-sm font-medium mb-2">Monthly Usage</p>
                      <div className="h-4 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary rounded-full" 
                          style={{ width: '45%' }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>0</span>
                        <span>45% of monthly limit</span>
                        <span>100%</span>
                      </div>
                    </div>
                    
                    <div className="pt-4 flex justify-center">
                      <Button asChild>
                        <Link to="/billing" className="flex items-center gap-2">
                          <CreditCard className="h-4 w-4" />
                          View Billing & Subscription
                        </Link>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default Dashboard; 