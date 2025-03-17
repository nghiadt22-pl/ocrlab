import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderIcon, 
  SearchIcon, 
  CreditCard, 
  Settings, 
  FileTextIcon,
  ChevronLeft,
  ChevronRight,
  LogOut
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface SidebarProps {
  collapsed: boolean;
  toggleSidebar: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, toggleSidebar }) => {
  const location = useLocation();
  const { signOut } = useAuth();
  const { user } = useUser();
  
  const initials = user?.firstName && user?.lastName 
    ? `${user.firstName[0]}${user.lastName[0]}`
    : user?.firstName?.[0] || 'U';

  const navItems = [
    {
      title: 'Dashboard',
      icon: <LayoutDashboard className="h-5 w-5" />,
      path: '/dashboard',
      active: location.pathname === '/dashboard'
    },
    {
      title: 'Folders',
      icon: <FolderIcon className="h-5 w-5" />,
      path: '/folders',
      active: location.pathname === '/folders' || location.pathname.startsWith('/folders/')
    },
    {
      title: 'Search',
      icon: <SearchIcon className="h-5 w-5" />,
      path: '/search',
      active: location.pathname === '/search'
    },
    {
      title: 'Billing',
      icon: <CreditCard className="h-5 w-5" />,
      path: '/billing',
      active: location.pathname === '/billing'
    },
    {
      title: 'Preferences',
      icon: <Settings className="h-5 w-5" />,
      path: '/preferences',
      active: location.pathname === '/preferences'
    }
  ];

  return (
    <div 
      className={cn(
        "h-screen fixed left-0 top-0 z-40 flex flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo and collapse button */}
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        <Link to="/" className="flex items-center space-x-2">
          <div className="bg-sidebar-accent/20 p-2 rounded-lg">
            <FileTextIcon className="h-6 w-6 text-sidebar-accent" />
          </div>
          {!collapsed && (
            <h1 className="text-xl font-medium text-sidebar-foreground">OCR LAB</h1>
          )}
        </Link>
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={toggleSidebar}
          className="text-sidebar-foreground hover:bg-sidebar-accent/20"
        >
          {collapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <TooltipProvider key={item.path} delayDuration={collapsed ? 100 : 1000}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  to={item.path}
                  className={cn(
                    "flex items-center rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                    item.active 
                      ? "bg-sidebar-accent text-sidebar-accent-foreground" 
                      : "text-sidebar-foreground/80 hover:bg-sidebar-accent/20 hover:text-sidebar-foreground"
                  )}
                >
                  <span className="mr-3">{item.icon}</span>
                  {!collapsed && <span>{item.title}</span>}
                </Link>
              </TooltipTrigger>
              {collapsed && (
                <TooltipContent side="right">
                  {item.title}
                </TooltipContent>
              )}
            </Tooltip>
          </TooltipProvider>
        ))}
      </nav>

      {/* User profile */}
      <div className="p-4 border-t border-sidebar-border">
        <TooltipProvider delayDuration={collapsed ? 100 : 1000}>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className={cn(
                "flex items-center",
                collapsed ? "justify-center" : "justify-between"
              )}>
                <div className="flex items-center space-x-3">
                  <Avatar className="h-8 w-8 border border-sidebar-border">
                    <AvatarImage src={user?.imageUrl} />
                    <AvatarFallback className="bg-sidebar-accent/20 text-sidebar-accent">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  {!collapsed && (
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">{user?.fullName || 'User'}</span>
                      <span className="text-xs text-sidebar-foreground/70">{user?.primaryEmailAddress?.emailAddress}</span>
                    </div>
                  )}
                </div>
                {!collapsed && (
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={() => signOut()}
                    className="text-sidebar-foreground/70 hover:bg-sidebar-accent/20 hover:text-sidebar-foreground"
                  >
                    <LogOut className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </TooltipTrigger>
            {collapsed && (
              <TooltipContent side="right">
                {user?.fullName || 'User'}
              </TooltipContent>
            )}
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  );
};

export default Sidebar; 