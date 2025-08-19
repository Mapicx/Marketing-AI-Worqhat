import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { MessageSquare, Sparkles, Copy } from "lucide-react";
import { useAppContext } from "@/contexts/AppContext";
import { generateSlogan } from "@/services/api";
import { toast } from "sonner";

const SloganGenerator = () => {
  const { forecastResults, isLoading, setIsLoading } = useAppContext();
  const [context, setContext] = useState("");
  const [slogans, setSlogans] = useState<string[]>([]);

  // Auto-fill context when forecast results are available
  const generateContextFromForecast = () => {
    if (forecastResults) {
      const campaignContext = `Campaign Type: ${forecastResults.recommended_campaign_type}\nOffer: ${forecastResults.recommended_offer}\nTarget Audience: ${forecastResults.campaign_details.target}\nDiscount: ${forecastResults.campaign_details.discount}%\nBudget: $${forecastResults.campaign_details.budget}`;
      setContext(campaignContext);
    } else {
      toast.error("No forecast results available. Please run a forecast first.");
    }
  };

  const handleGenerateSlogans = async () => {
    if (!context.trim()) {
      toast.error("Please enter context for slogan generation");
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateSlogan({ context });
      
      if (response.slogans && Array.isArray(response.slogans)) {
        setSlogans(response.slogans);
        toast.success("Slogans generated successfully!");
      } else {
        toast.error("Failed to generate slogans. Please try again.");
      }
    } catch (error) {
      console.error("Slogan generation error:", error);
      toast.error("Failed to generate slogans. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (slogan: string) => {
    navigator.clipboard.writeText(slogan);
    toast.success("Slogan copied to clipboard!");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Slogan Generator</h1>
        <p className="text-muted-foreground mt-2">
          Create compelling campaign slogans powered by artificial intelligence
        </p>
      </div>

      {/* Input Section */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Campaign Context
          </CardTitle>
          <CardDescription>
            Provide context about your campaign for targeted slogan generation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="context">Campaign Details</Label>
            <Textarea
              id="context"
              placeholder="Describe your campaign, target audience, product/service, and key messaging..."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              rows={5}
              className="resize-none"
            />
          </div>

          <div className="flex gap-3">
            <Button
              onClick={handleGenerateSlogans}
              disabled={!context.trim() || isLoading}
              className="shadow-elegant"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Generate Slogans
                </>
              )}
            </Button>

            {forecastResults && (
              <Button
                variant="outline"
                onClick={generateContextFromForecast}
                disabled={isLoading}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Use Forecast Data
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Forecast Data Preview */}
      {forecastResults && (
        <Card className="shadow-card border-primary/20">
          <CardHeader>
            <CardTitle className="text-lg">Available Forecast Data</CardTitle>
            <CardDescription>
              Click "Use Forecast Data" to auto-fill context with campaign details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="font-medium text-muted-foreground">Campaign Type:</span>
                <p>{forecastResults.recommended_campaign_type}</p>
              </div>
              <div>
                <span className="font-medium text-muted-foreground">Offer:</span>
                <p>{forecastResults.recommended_offer}</p>
              </div>
              <div>
                <span className="font-medium text-muted-foreground">Target:</span>
                <p>{forecastResults.campaign_details.target}</p>
              </div>
              <div>
                <span className="font-medium text-muted-foreground">Success Rate:</span>
                <p>{Math.round(forecastResults.success_probability)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generated Slogans */}
      {slogans.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Generated Campaign Slogans</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {slogans.map((slogan, index) => (
              <Card 
                key={index} 
                className="shadow-card hover:shadow-elegant transition-smooth cursor-pointer group"
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-lg font-medium leading-relaxed group-hover:text-primary transition-smooth">
                        "{slogan}"
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(slogan)}
                      className="opacity-0 group-hover:opacity-100 transition-smooth"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Tips Section */}
      <Card className="shadow-card bg-gradient-hero">
        <CardHeader>
          <CardTitle>💡 Slogan Generation Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li>• Include your brand name and core value proposition</li>
            <li>• Mention your target audience and their pain points</li>
            <li>• Describe the emotions you want to evoke</li>
            <li>• Specify the tone (professional, playful, urgent, inspiring)</li>
            <li>• Include key benefits or unique selling points</li>
            <li>• Mention any specific industry or market context</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default SloganGenerator;