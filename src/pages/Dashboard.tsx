import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileIcon, FolderIcon, UploadIcon, BarChart3, PieChart, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  // Mock data for dashboard
  const stats = {
    totalFiles: 128,
    totalFolders: 12,
    pagesProcessed: 1024,
    queriesRun: 256,
    storageUsed: 2.4, // GB
    storageLimit: 5, // GB
    recentFiles: [
      { id: 1, name: 'Financial Report 2023.pdf', folder: 'Finance', status: 'complete', date: '2023-12-15' },
      { id: 2, name: 'Meeting Minutes.pdf', folder: 'Meetings', status: 'complete', date: '2023-12-10' },
      { id: 3, name: 'Product Specifications.pdf', folder: 'Products', status: 'processing', date: '2023-12-05' },
      { id: 4, name: 'Customer Feedback.pdf', folder: 'Feedback', status: 'queued', date: '2023-12-01' },
    ],
    processingQueue: [
      { id: 3, name: 'Product Specifications.pdf', progress: 65, status: 'processing' },
      { id: 4, name: 'Customer Feedback.pdf', progress: 0, status: 'queued' },
    ]
  };

  // Calculate storage percentage
  const storagePercentage = (stats.storageUsed / stats.storageLimit) * 100;

  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Welcome back</h2>
          <p className="text-muted-foreground">Here's an overview of your document processing activity</p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-2">
          <Button asChild>
            <Link to="/folders">
              <FolderIcon className="mr-2 h-4 w-4" />
              Browse Folders
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/search">
              <FileIcon className="mr-2 h-4 w-4" />
              Search Documents
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Files</CardTitle>
            <FileIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalFiles}</div>
            <p className="text-xs text-muted-foreground">
              Across {stats.totalFolders} folders
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pages Processed</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pagesProcessed}</div>
            <p className="text-xs text-muted-foreground">
              +24 in the last 7 days
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Queries Run</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.queriesRun}</div>
            <p className="text-xs text-muted-foreground">
              +12 in the last 7 days
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <FileIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold">{stats.storageUsed} GB</div>
              <div className="text-sm text-muted-foreground">/ {stats.storageLimit} GB</div>
            </div>
            <Progress value={storagePercentage} className="h-2 mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Recent activity and processing queue */}
      <Tabs defaultValue="recent" className="space-y-4">
        <TabsList>
          <TabsTrigger value="recent">Recent Files</TabsTrigger>
          <TabsTrigger value="processing">Processing Queue</TabsTrigger>
        </TabsList>
        <TabsContent value="recent" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {stats.recentFiles.map((file) => (
              <Card key={file.id} className="overflow-hidden">
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-medium truncate">{file.name}</CardTitle>
                    <Button variant="ghost" size="icon" asChild>
                      <Link to={`/folders/${file.folder.toLowerCase()}/${file.id}`}>
                        <ArrowUpRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                  <CardDescription className="flex items-center">
                    <FolderIcon className="h-3 w-3 mr-1" />
                    {file.folder}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-4 pt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{file.date}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      file.status === 'complete' 
                        ? 'bg-success/20 text-success' 
                        : file.status === 'processing' 
                          ? 'bg-warning/20 text-warning' 
                          : 'bg-muted text-muted-foreground'
                    }`}>
                      {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="flex justify-center">
            <Button variant="outline" asChild>
              <Link to="/folders">View All Files</Link>
            </Button>
          </div>
        </TabsContent>
        <TabsContent value="processing" className="space-y-4">
          {stats.processingQueue.length > 0 ? (
            <div className="space-y-4">
              {stats.processingQueue.map((file) => (
                <Card key={file.id} className="overflow-hidden">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base font-medium">{file.name}</CardTitle>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        file.status === 'processing' 
                          ? 'bg-warning/20 text-warning' 
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-2">
                    {file.status === 'processing' && (
                      <>
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-muted-foreground">Progress</span>
                          <span>{file.progress}%</span>
                        </div>
                        <Progress value={file.progress} className="h-2" />
                      </>
                    )}
                    {file.status === 'queued' && (
                      <div className="text-sm text-muted-foreground">
                        Waiting to be processed...
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <div className="flex flex-col items-center justify-center space-y-4">
                  <UploadIcon className="h-8 w-8 text-muted-foreground" />
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">No files in queue</h3>
                    <p className="text-sm text-muted-foreground">
                      Upload new documents to start processing
                    </p>
                  </div>
                  <Button asChild>
                    <Link to="/folders">
                      <UploadIcon className="mr-2 h-4 w-4" />
                      Upload Files
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard; 