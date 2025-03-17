import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  FolderIcon, 
  PlusIcon, 
  SearchIcon, 
  MoreHorizontal, 
  FolderPlusIcon,
  Trash2,
  Edit,
  Share
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

// Mock data for folders
const mockFolders = [
  { id: 1, name: 'Finance', files: 12, lastUpdated: '2023-12-15' },
  { id: 2, name: 'Contracts', files: 8, lastUpdated: '2023-12-10' },
  { id: 3, name: 'Invoices', files: 24, lastUpdated: '2023-12-05' },
  { id: 4, name: 'Reports', files: 6, lastUpdated: '2023-12-01' },
  { id: 5, name: 'HR Documents', files: 15, lastUpdated: '2023-11-28' },
  { id: 6, name: 'Marketing', files: 9, lastUpdated: '2023-11-25' },
];

const Folders: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  
  // Filter folders based on search query
  const filteredFolders = mockFolders.filter(folder => 
    folder.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Handle folder creation
  const handleCreateFolder = (e: React.FormEvent) => {
    e.preventDefault();
    if (newFolderName.trim()) {
      // In a real app, this would call an API to create the folder
      console.log('Creating folder:', newFolderName);
      setNewFolderName('');
      setIsCreateDialogOpen(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Folders</h2>
          <p className="text-muted-foreground">Organize and manage your document folders</p>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="relative w-full md:w-64">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search folders..." 
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <PlusIcon className="h-4 w-4 mr-2" />
                New Folder
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Folder</DialogTitle>
                <DialogDescription>
                  Enter a name for your new folder to organize your documents.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateFolder}>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Folder Name</Label>
                    <Input 
                      id="name" 
                      placeholder="Enter folder name" 
                      value={newFolderName}
                      onChange={(e) => setNewFolderName(e.target.value)}
                      autoFocus
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Create Folder</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      
      {/* Folders grid */}
      {filteredFolders.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredFolders.map((folder) => (
            <Card key={folder.id} className="overflow-hidden card-hover">
              <Link to={`/folders/${folder.id}`} className="block h-full">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="bg-primary/10 p-3 rounded-lg">
                        <FolderIcon className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium text-lg">{folder.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {folder.files} {folder.files === 1 ? 'file' : 'files'}
                        </p>
                      </div>
                    </div>
                    
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e) => e.preventDefault()}>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem className="cursor-pointer">
                          <Edit className="h-4 w-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuItem className="cursor-pointer">
                          <Share className="h-4 w-4 mr-2" />
                          Share
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="cursor-pointer text-destructive">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardContent>
                <CardFooter className="p-4 pt-0 border-t bg-muted/30">
                  <p className="text-xs text-muted-foreground">
                    Last updated on {folder.lastUpdated}
                  </p>
                </CardFooter>
              </Link>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="bg-muted p-4 rounded-full">
            <FolderPlusIcon className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-medium">No folders found</h3>
          {searchQuery ? (
            <p className="text-muted-foreground text-center max-w-md">
              No folders match your search query. Try a different search or create a new folder.
            </p>
          ) : (
            <p className="text-muted-foreground text-center max-w-md">
              You haven't created any folders yet. Create a folder to start organizing your documents.
            </p>
          )}
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Folder
          </Button>
        </div>
      )}
    </div>
  );
};

export default Folders; 