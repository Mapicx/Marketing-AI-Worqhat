import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Upload, BarChart3, Download, FileText } from "lucide-react";
import { useAppContext } from "@/contexts/AppContext";
import { runForecast } from "@/services/api";
import { toast } from "sonner";

const Forecast = () => {
  const { forecastResults, setForecastResults, isLoading, setIsLoading } = useAppContext();
  const [customersFile, setCustomersFile] = useState<File | null>(null);
  const [campaignHistoryFile, setCampaignHistoryFile] = useState<File | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'customers' | 'campaign') => {
    const file = e.target.files?.[0];
    if (file) {
      if (type === 'customers') {
        setCustomersFile(file);
      } else {
        setCampaignHistoryFile(file);
      }
    }
  };

  const handleRunForecast = async () => {
    if (!customersFile || !campaignHistoryFile) {
      toast.error("Please upload both CSV files");
      return;
    }

    setIsLoading(true);
    try {
      const response = await runForecast({
        customers_file: customersFile,
        campaign_history_file: campaignHistoryFile,
      });

      if (response.status === "success" && response.results) {
        setForecastResults(response.results);
        toast.success("Forecast completed successfully!");
      } else {
        toast.error("Forecast failed. Please try again.");
      }
    } catch (error) {
      console.error("Forecast error:", error);
      toast.error("Failed to run forecast. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Predictive Analytics</h1>
        <p className="text-muted-foreground mt-2">
          Upload your customer and campaign data to generate AI-powered forecasts
        </p>
      </div>

      {/* File Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              Customer Data
            </CardTitle>
            <CardDescription>
              Upload your customers.csv file containing customer information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Label htmlFor="customers-file">Customers CSV File</Label>
              <Input
                id="customers-file"
                type="file"
                accept=".csv"
                onChange={(e) => handleFileUpload(e, 'customers')}
                className="cursor-pointer"
              />
              {customersFile && (
                <p className="text-sm text-success">
                  ✅ {customersFile.name} uploaded
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              Campaign History
            </CardTitle>
            <CardDescription>
              Upload your campaign_history.csv file with past campaign data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Label htmlFor="campaign-file">Campaign History CSV File</Label>
              <Input
                id="campaign-file"
                type="file"
                accept=".csv"
                onChange={(e) => handleFileUpload(e, 'campaign')}
                className="cursor-pointer"
              />
              {campaignHistoryFile && (
                <p className="text-sm text-success">
                  ✅ {campaignHistoryFile.name} uploaded
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Run Forecast Button */}
      <div className="flex justify-center">
        <Button
          onClick={handleRunForecast}
          disabled={!customersFile || !campaignHistoryFile || isLoading}
          size="lg"
          className="shadow-elegant"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
              Running Forecast...
            </>
          ) : (
            <>
              <BarChart3 className="h-5 w-5 mr-2" />
              Run Forecast
            </>
          )}
        </Button>
      </div>

      {/* Results Section */}
      {forecastResults && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Forecast Results</h2>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Segment Count
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{forecastResults.segment_count}</div>
              </CardContent>
            </Card>

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Recommended Campaign
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-semibold">
                  {forecastResults.recommended_campaign_type}
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Privacy Compliance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-semibold">
                  {forecastResults.privacy_compliance ? "✅ Compliant" : "❌ Review Required"}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Success Probability */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Success Probability</CardTitle>
              <CardDescription>
                Predicted likelihood of campaign success
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Success Rate</span>
                  <span>{Math.round(forecastResults.success_probability)}%</span>
                </div>
                <Progress value={forecastResults.success_probability} className="h-3" />
              </div>
            </CardContent>
          </Card>

          {/* Campaign Details */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Campaign Details</CardTitle>
              <CardDescription>
                Recommended campaign configuration
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Type</Label>
                  <p className="font-semibold">{forecastResults.campaign_details.type}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Offer</Label>
                  <p className="font-semibold">{forecastResults.campaign_details.offer}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Target</Label>
                  <p className="font-semibold">{forecastResults.campaign_details.target}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Discount</Label>
                  <p className="font-semibold">{forecastResults.campaign_details.discount}%</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Budget</Label>
                  <p className="font-semibold">${forecastResults.campaign_details.budget}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Target Size</Label>
                  <p className="font-semibold">{forecastResults.campaign_details.target_size}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Report Links */}
          {(forecastResults.report_links.html || forecastResults.report_links.pdf) && (
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>Download Reports</CardTitle>
                <CardDescription>
                  Access detailed forecast reports
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4">
                  {forecastResults.report_links.pdf && (
                    <Button asChild variant="outline">
                      <a href={forecastResults.report_links.pdf} target="_blank" rel="noopener noreferrer">
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF Report
                      </a>
                    </Button>
                  )}
                  {forecastResults.report_links.html && (
                    <Button asChild variant="outline">
                      <a href={forecastResults.report_links.html} target="_blank" rel="noopener noreferrer">
                        <FileText className="h-4 w-4 mr-2" />
                        View HTML Report
                      </a>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default Forecast;