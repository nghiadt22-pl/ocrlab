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
  Share,
  Loader2
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
import { useFolders } from '@/hooks/use-api';
import { useToast } from '@/components/ui/use-toast';
import { format } from 'date-fns';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const Folders: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [folderToDelete, setFolderToDelete] = useState<number | null>(null);
  const { toast } = useToast();
  
  // Use the folders API hook
  const { 
    folders, 
    isLoading, 
    isError, 
    error, 
    createFolder, 
    deleteFolder,
    isCreating,
    isDeleting
  } = useFolders();
  
  // Filter folders based on search query
  const filteredFolders = folders.filter(folder => 
    folder.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Handle folder creation
  const handleCreateFolder = (e: React.FormEvent) => {
    e.preventDefault();
    if (newFolderName.trim()) {
      createFolder(newFolderName.trim());
      setNewFolderName('');
      setIsCreateDialogOpen(false);
    }
  };

  // Handle folder deletion
  const handleDeleteFolder = () => {
    if (folderToDelete !== null) {
      deleteFolder(folderToDelete);
      setFolderToDelete(null);
    }
  };

  // Show error if API call fails
  if (isError && error) {
    toast({
      title: 'Error loading folders',
      description: error.message,
      variant: 'destructive',
    });
  }

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
                  <Button type="submit" disabled={isCreating}>
                    {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create Folder
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      
      {/* Loading state */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}
      
      {/* Folders grid */}
      {!isLoading && filteredFolders.length > 0 && (
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
                          Created on {format(new Date(folder.created_at), 'MMM d, yyyy')}
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
                        <DropdownMenuItem 
                          className="cursor-pointer text-destructive"
                          onClick={(e) => {
                            e.preventDefault();
                            setFolderToDelete(folder.id);
                          }}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardContent>
                <CardFooter className="p-4 pt-0 border-t bg-muted/30">
                  <p className="text-xs text-muted-foreground">
                    Last updated on {format(new Date(folder.updated_at), 'MMM d, yyyy')}
                  </p>
                </CardFooter>
              </Link>
            </Card>
          ))}
        </div>
      )}
      
      {/* Empty state */}
      {!isLoading && filteredFolders.length === 0 && (
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
      
      {/* Delete confirmation dialog */}
      <AlertDialog open={folderToDelete !== null} onOpenChange={(open) => !open && setFolderToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this folder and all its contents. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteFolder}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Folders; 