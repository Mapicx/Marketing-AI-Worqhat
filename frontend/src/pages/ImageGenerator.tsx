import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Image, Sparkles, Download } from "lucide-react";
import { useAppContext } from "@/contexts/AppContext";
import { generateImage } from "@/services/api";
import { toast } from "sonner";

const ImageGenerator = () => {
  const { forecastResults, isLoading, setIsLoading } = useAppContext();
  const [prompt, setPrompt] = useState("");
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);

  // Auto-fill prompt when forecast results are available
  const generatePromptFromForecast = () => {
    if (forecastResults) {
      const campaignPrompt = `Create a marketing image for a ${forecastResults.recommended_campaign_type} campaign with ${forecastResults.recommended_offer}. Target audience: ${forecastResults.campaign_details.target}. Professional, modern design with engaging visuals.`;
      setPrompt(campaignPrompt);
    } else {
      toast.error("No forecast results available. Please run a forecast first.");
    }
  };

  const handleGenerateImage = async () => {
    if (!prompt.trim()) {
      toast.error("Please enter a prompt for image generation");
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateImage({ prompt });
      
      if (response.image_url) {
        setGeneratedImage(response.image_url);
        toast.success("Image generated successfully!");
      } else {
        toast.error("Failed to generate image. Please try again.");
      }
    } catch (error) {
      console.error("Image generation error:", error);
      toast.error("Failed to generate image. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Image Generator</h1>
        <p className="text-muted-foreground mt-2">
          Generate compelling marketing visuals using AI-powered image generation
        </p>
      </div>

      {/* Input Section */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Image Prompt
          </CardTitle>
          <CardDescription>
            Describe the marketing image you want to create
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="prompt">Image Description</Label>
            <Textarea
              id="prompt"
              placeholder="Describe the marketing image you want to generate..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="flex gap-3">
            <Button
              onClick={handleGenerateImage}
              disabled={!prompt.trim() || isLoading}
              className="shadow-elegant"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <Image className="h-4 w-4 mr-2" />
                  Generate Image
                </>
              )}
            </Button>

            {forecastResults && (
              <Button
                variant="outline"
                onClick={generatePromptFromForecast}
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
              Click "Use Forecast Data" to auto-fill prompt with campaign details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
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
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generated Image Display */}
      {generatedImage && (
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Image className="h-5 w-5 text-primary" />
              Generated Marketing Image
            </CardTitle>
            <CardDescription>
              Your AI-generated marketing visual
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="relative">
                <img
                  src={generatedImage}
                  alt="Generated marketing image"
                  className="w-full max-w-2xl mx-auto rounded-lg shadow-elegant"
                />
              </div>
              
              <div className="flex justify-center">
                <Button asChild variant="outline">
                  <a href={generatedImage} download="marketing-image.jpg">
                    <Download className="h-4 w-4 mr-2" />
                    Download Image
                  </a>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tips Section */}
      <Card className="shadow-card bg-gradient-hero">
        <CardHeader>
          <CardTitle>💡 Image Generation Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li>• Be specific about style, colors, and visual elements</li>
            <li>• Include your target audience demographics</li>
            <li>• Mention the product or service being promoted</li>
            <li>• Specify the desired mood or emotion (professional, friendly, urgent)</li>
            <li>• Include brand positioning terms (premium, affordable, innovative)</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default ImageGenerator;