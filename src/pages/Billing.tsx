import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { 
  CreditCard, 
  Receipt, 
  Calendar, 
  ArrowUpCircle, 
  CheckCircle2,
  AlertCircle,
  Download,
  BadgeDollarSign,
  Wallet
} from 'lucide-react';
import Header from '@/components/Header';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

// Mock data for billing information
const mockBillingData = {
  currentPlan: 'Professional',
  billingCycle: 'Monthly',
  nextBillingDate: 'April 10, 2025',
  amount: '$29.99',
  paymentMethod: 'Visa ending in 4242',
  usageLimit: {
    pagesPerMonth: 1000,
    storageGB: 10,
    apiCalls: 5000
  },
  currentUsage: {
    pagesProcessed: 450,
    storageUsed: 3.2,
    apiCalls: 1250
  },
  invoices: [
    { id: 'INV-001', date: 'March 10, 2025', amount: '$29.99', status: 'Paid' },
    { id: 'INV-002', date: 'February 10, 2025', amount: '$29.99', status: 'Paid' },
    { id: 'INV-003', date: 'January 10, 2025', amount: '$29.99', status: 'Paid' }
  ],
  plans: [
    { 
      name: 'Basic', 
      price: '$9.99/month', 
      features: [
        '100 pages per month',
        '2GB storage',
        'Basic OCR features',
        'Email support'
      ]
    },
    { 
      name: 'Professional', 
      price: '$29.99/month', 
      features: [
        '1,000 pages per month',
        '10GB storage',
        'Advanced OCR features',
        'Priority support',
        'API access'
      ],
      current: true
    },
    { 
      name: 'Enterprise', 
      price: '$99.99/month', 
      features: [
        'Unlimited pages',
        '50GB storage',
        'All OCR features',
        '24/7 support',
        'Advanced API access',
        'Custom integrations'
      ]
    }
  ]
};

const Billing: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [autoRenew, setAutoRenew] = useState<boolean>(true);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-24">
        <div className="flex flex-col gap-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Billing & Subscription</h1>
            <p className="text-muted-foreground">
              Manage your subscription, payment methods, and billing history.
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid grid-cols-3 w-full max-w-md">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="invoices">Invoices</TabsTrigger>
              <TabsTrigger value="plans">Plans</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BadgeDollarSign className="h-5 w-5 text-primary" />
                      Current Plan
                    </CardTitle>
                    <CardDescription>Your subscription details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Plan</span>
                      <Badge variant="secondary" className="text-sm">
                        {mockBillingData.currentPlan}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Billing Cycle</span>
                      <span className="text-sm">{mockBillingData.billingCycle}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Next Billing Date</span>
                      <span className="text-sm">{mockBillingData.nextBillingDate}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Amount</span>
                      <span className="text-sm font-bold">{mockBillingData.amount}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Auto-renew</span>
                      <div className="flex items-center space-x-2">
                        <Switch 
                          id="auto-renew" 
                          checked={autoRenew} 
                          onCheckedChange={setAutoRenew} 
                        />
                        <Label htmlFor="auto-renew" className="text-sm">
                          {autoRenew ? 'On' : 'Off'}
                        </Label>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button variant="outline">Change Plan</Button>
                    <Button variant="destructive">Cancel Subscription</Button>
                  </CardFooter>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CreditCard className="h-5 w-5 text-primary" />
                      Payment Method
                    </CardTitle>
                    <CardDescription>Manage your payment details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-4 p-4 border rounded-lg">
                      <div className="bg-primary/10 p-2 rounded-full">
                        <CreditCard className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{mockBillingData.paymentMethod}</p>
                        <p className="text-xs text-muted-foreground">Expires 12/2026</p>
                      </div>
                      <Badge>Default</Badge>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Button variant="outline" className="w-full">Update Payment Method</Button>
                  </CardFooter>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wallet className="h-5 w-5 text-primary" />
                    Usage & Limits
                  </CardTitle>
                  <CardDescription>Monitor your current usage against plan limits</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Pages Processed</span>
                      <span>{mockBillingData.currentUsage.pagesProcessed} / {mockBillingData.usageLimit.pagesPerMonth}</span>
                    </div>
                    <Progress value={(mockBillingData.currentUsage.pagesProcessed / mockBillingData.usageLimit.pagesPerMonth) * 100} />
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Storage Used (GB)</span>
                      <span>{mockBillingData.currentUsage.storageUsed} / {mockBillingData.usageLimit.storageGB}</span>
                    </div>
                    <Progress value={(mockBillingData.currentUsage.storageUsed / mockBillingData.usageLimit.storageGB) * 100} />
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>API Calls</span>
                      <span>{mockBillingData.currentUsage.apiCalls} / {mockBillingData.usageLimit.apiCalls}</span>
                    </div>
                    <Progress value={(mockBillingData.currentUsage.apiCalls / mockBillingData.usageLimit.apiCalls) * 100} />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="invoices" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Receipt className="h-5 w-5 text-primary" />
                    Billing History
                  </CardTitle>
                  <CardDescription>View and download your past invoices</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Invoice</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mockBillingData.invoices.map((invoice) => (
                        <TableRow key={invoice.id}>
                          <TableCell className="font-medium">{invoice.id}</TableCell>
                          <TableCell>{invoice.date}</TableCell>
                          <TableCell>{invoice.amount}</TableCell>
                          <TableCell>
                            <Badge 
                              variant={invoice.status === 'Paid' ? 'secondary' : 'destructive'}
                              className="bg-green-100 text-green-800 hover:bg-green-100"
                            >
                              {invoice.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="plans" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {mockBillingData.plans.map((plan) => (
                  <Card key={plan.name} className={plan.current ? 'border-primary' : ''}>
                    <CardHeader>
                      <CardTitle>{plan.name}</CardTitle>
                      <CardDescription>{plan.price}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                            <span className="text-sm">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                    <CardFooter>
                      {plan.current ? (
                        <Button className="w-full" disabled>
                          Current Plan
                        </Button>
                      ) : (
                        <Button variant="outline" className="w-full">
                          Switch to {plan.name}
                        </Button>
                      )}
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default Billing; 