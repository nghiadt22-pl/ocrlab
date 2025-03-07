import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FolderIcon, FolderPlusIcon, MoreHorizontalIcon, FileIcon, TrashIcon, PencilIcon } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import Header from '@/components/Header';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';

// Mock data for folders
const mockFolders = [
  {
    id: '1',
    name: 'Home',
    documentCount: 5,
    createdAt: new Date('2023-01-15'),
  },
  {
    id: '2',
    name: 'Financial Reports',
    documentCount: 12,
    createdAt: new Date('2023-02-20'),
  },
  {
    id: '3',
    name: 'Contracts',
    documentCount: 8,
    createdAt: new Date('2023-03-10'),
  },
  {
    id: '4',
    name: 'Meeting Notes',
    documentCount: 3,
    createdAt: new Date('2023-04-05'),
  },
];

const Folders: React.FC = () => {
  const [folders, setFolders] = useState(mockFolders);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [folderToRename, setFolderToRename] = useState<{ id: string, name: string } | null>(null);
  const [renameFolderName, setRenameFolderName] = useState('');

  const handleCreateFolder = () => {
    if (!newFolderName.trim()) {
      toast.error('Folder name cannot be empty');
      return;
    }

    const newFolder = {
      id: Date.now().toString(),
      name: newFolderName,
      documentCount: 0,
      createdAt: new Date(),
    };

    setFolders([...folders, newFolder]);
    setNewFolderName('');
    setIsCreateDialogOpen(false);
    toast.success(`Folder "${newFolderName}" created successfully`);
  };

  const handleDeleteFolder = (folderId: string, folderName: string) => {
    setFolders(folders.filter(folder => folder.id !== folderId));
    toast.success(`Folder "${folderName}" deleted successfully`);
  };

  const openRenameDialog = (folder: { id: string, name: string }) => {
    setFolderToRename(folder);
    setRenameFolderName(folder.name);
    setIsRenameDialogOpen(true);
  };

  const handleRenameFolder = () => {
    if (!renameFolderName.trim() || !folderToRename) {
      toast.error('Folder name cannot be empty');
      return;
    }

    setFolders(folders.map(folder => 
      folder.id === folderToRename.id 
        ? { ...folder, name: renameFolderName } 
        : folder
    ));
    
    toast.success(`Folder renamed to "${renameFolderName}" successfully`);
    setIsRenameDialogOpen(false);
    setFolderToRename(null);
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Folders</h1>
            <p className="text-muted-foreground">
              Organize your documents into folders for easy access
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <FolderPlusIcon className="h-4 w-4" />
                Create Folder
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Folder</DialogTitle>
                <DialogDescription>
                  Enter a name for your new folder
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <Label htmlFor="folderName">Folder Name</Label>
                <Input 
                  id="folderName" 
                  value={newFolderName} 
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="e.g., Financial Reports"
                  className="mt-2"
                />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateFolder}>
                  Create Folder
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {folders.map((folder) => (
            <Card key={folder.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <div className="bg-primary/10 p-2 rounded-lg">
                      <FolderIcon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{folder.name}</CardTitle>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontalIcon className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem 
                        className="flex items-center gap-2 cursor-pointer"
                        onClick={() => openRenameDialog({ id: folder.id, name: folder.name })}
                      >
                        <PencilIcon className="h-4 w-4" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="flex items-center gap-2 text-destructive cursor-pointer"
                        onClick={() => handleDeleteFolder(folder.id, folder.name)}
                      >
                        <TrashIcon className="h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <CardDescription>
                  Created on {formatDate(folder.createdAt)}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-3">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileIcon className="h-4 w-4" />
                  <span>{folder.documentCount} document{folder.documentCount !== 1 ? 's' : ''}</span>
                </div>
              </CardContent>
              <CardFooter className="pt-0">
                <Button variant="outline" className="w-full" asChild>
                  <Link to={`/folders/${folder.id}`}>Open Folder</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Rename Folder Dialog */}
        <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Rename Folder</DialogTitle>
              <DialogDescription>
                Enter a new name for "{folderToRename?.name}"
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Label htmlFor="renameFolderName">New Folder Name</Label>
              <Input 
                id="renameFolderName" 
                value={renameFolderName} 
                onChange={(e) => setRenameFolderName(e.target.value)}
                className="mt-2"
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsRenameDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleRenameFolder}>
                Rename Folder
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
};

export default Folders; 