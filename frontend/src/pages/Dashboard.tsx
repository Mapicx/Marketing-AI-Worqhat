import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart3, Image, MessageSquare, Youtube, TrendingUp, Users, Target, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { useAppContext } from "@/contexts/AppContext";
import { Progress } from "@/components/ui/progress";
import dashboardHero from "@/assets/dashboard-hero.jpg";

const Dashboard = () => {
  const { forecastResults } = useAppContext();

  const quickActions = [
    {
      title: "Run Forecast",
      description: "Analyze customer data and predict campaign success",
      icon: BarChart3,
      link: "/forecast",
      color: "bg-primary",
    },
    {
      title: "Generate Images",
      description: "Create AI-powered marketing visuals",
      icon: Image,
      link: "/image-generator", 
      color: "bg-secondary",
    },
    {
      title: "Create Slogans",
      description: "Generate compelling campaign slogans",
      icon: MessageSquare,
      link: "/slogan-generator",
      color: "bg-success",
    },
    {
      title: "YouTube QA",
      description: "Analyze and query YouTube content",
      icon: Youtube,
      link: "/youtube-qa",
      color: "bg-warning",
    },
  ];

  const stats = [
    {
      title: "Total Campaigns",
      value: "12",
      change: "+23%",
      icon: Target,
    },
    {
      title: "Success Rate",
      value: forecastResults ? `${Math.round(forecastResults.success_probability)}%` : "78%",
      change: "+12%",
      icon: TrendingUp,
    },
    {
      title: "Active Segments",
      value: forecastResults ? forecastResults.segment_count.toString() : "8",
      change: "+5%",
      icon: Users,
    },
    {
      title: "AI Insights",
      value: "24",
      change: "+18%",
      icon: Zap,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-xl bg-gradient-primary p-8 text-white">
        <div className="absolute inset-0 opacity-20">
          <img 
            src={dashboardHero} 
            alt="AI Marketing Dashboard" 
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl font-bold mb-4">
            Welcome to TechNeeti Marketing AI
          </h1>
          <p className="text-xl text-white/90 mb-6">
            Harness the power of artificial intelligence to supercharge your marketing campaigns
            and drive unprecedented growth.
          </p>
          <Button size="lg" variant="secondary" className="shadow-elegant">
            Get Started
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={stat.title} className="shadow-card hover:shadow-elegant transition-smooth">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-success">
                {stat.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Last Forecast Results */}
      {forecastResults && (
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              Latest Forecast Results
            </CardTitle>
            <CardDescription>
              Your most recent campaign prediction analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Recommended Campaign
                </label>
                <p className="text-lg font-semibold">
                  {forecastResults.recommended_campaign_type}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Target Segments
                </label>
                <p className="text-lg font-semibold">
                  {forecastResults.segment_count}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Privacy Compliance
                </label>
                <p className="text-lg font-semibold">
                  {forecastResults.privacy_compliance ? "✅ Compliant" : "❌ Review Required"}
                </p>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Success Probability</span>
                <span>{Math.round(forecastResults.success_probability)}%</span>
              </div>
              <Progress value={forecastResults.success_probability} className="h-2" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <Card 
              key={action.title} 
              className="shadow-card hover:shadow-elegant transition-smooth cursor-pointer group"
            >
              <Link to={action.link}>
                <CardHeader className="text-center">
                  <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-bounce`}>
                    <action.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-lg">{action.title}</CardTitle>
                  <CardDescription>{action.description}</CardDescription>
                </CardHeader>
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;