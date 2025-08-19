import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Youtube, MessageSquare, Play, HelpCircle } from "lucide-react";
import { processVideo, queryVideo } from "@/services/api";
import { toast } from "sonner";

interface VideoInfo {
  video_id: string;
  url: string;
  chunk_count: number;
  title?: string;
}

const YouTubeQA = () => {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [answer, setAnswer] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);

  const handleProcessVideo = async () => {
    if (!youtubeUrl.trim()) {
      toast.error("Please enter a YouTube URL");
      return;
    }

    // Basic YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;
    if (!youtubeRegex.test(youtubeUrl)) {
      toast.error("Please enter a valid YouTube URL");
      return;
    }

    setIsProcessing(true);
    try {
      const response = await processVideo({ youtube_url: youtubeUrl });
      
      if (response.video_info) {
        setVideoInfo(response.video_info);
        toast.success("Video processed successfully!");
      } else {
        toast.error("Failed to process video. Please try again.");
      }
    } catch (error) {
      console.error("Video processing error:", error);
      toast.error("Failed to process video. Please check the URL and try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      toast.error("Please enter a question");
      return;
    }

    if (!videoInfo) {
      toast.error("Please process a video first");
      return;
    }

    setIsQuerying(true);
    try {
      const response = await queryVideo({ question });
      
      if (response.answer) {
        setAnswer(response.answer);
        toast.success("Question answered successfully!");
      } else {
        toast.error("Failed to get answer. Please try again.");
      }
    } catch (error) {
      console.error("Query error:", error);
      toast.error("Failed to get answer. Please try again.");
    } finally {
      setIsQuerying(false);
    }
  };

  const getVideoThumbnail = (videoId: string) => {
    return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">YouTube QA System</h1>
        <p className="text-muted-foreground mt-2">
          Analyze YouTube videos and ask questions using AI-powered RAG technology
        </p>
      </div>

      {/* Video Processing Section */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Youtube className="h-5 w-5 text-red-500" />
            Process YouTube Video
          </CardTitle>
          <CardDescription>
            Enter a YouTube URL to analyze and prepare for Q&A
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="youtube-url">YouTube URL</Label>
            <Input
              id="youtube-url"
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
            />
          </div>

          <Button
            onClick={handleProcessVideo}
            disabled={!youtubeUrl.trim() || isProcessing}
            className="shadow-elegant"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Processing Video...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Process Video
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Video Info Display */}
      {videoInfo && (
        <Card className="shadow-card border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Youtube className="h-5 w-5 text-red-500" />
              Video Information
            </CardTitle>
            <CardDescription>
              Video has been processed and is ready for questions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <img
                  src={getVideoThumbnail(videoInfo.video_id)}
                  alt="Video thumbnail"
                  className="w-full aspect-video object-cover rounded-lg shadow-card"
                />
              </div>
              <div className="space-y-3">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Video ID</Label>
                  <p className="font-mono text-sm bg-muted p-2 rounded">{videoInfo.video_id}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">URL</Label>
                  <p className="text-sm text-primary">
                    <a href={videoInfo.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {videoInfo.url}
                    </a>
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Chunks Processed</Label>
                  <p className="text-lg font-semibold text-success">{videoInfo.chunk_count}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Question Section */}
      {videoInfo && (
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HelpCircle className="h-5 w-5 text-primary" />
              Ask Questions
            </CardTitle>
            <CardDescription>
              Ask questions about the video content using natural language
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="question">Your Question</Label>
              <Textarea
                id="question"
                placeholder="What is the main topic of this video? What are the key points discussed?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={3}
                className="resize-none"
              />
            </div>

            <Button
              onClick={handleAskQuestion}
              disabled={!question.trim() || isQuerying}
              className="shadow-elegant"
            >
              {isQuerying ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Getting Answer...
                </>
              ) : (
                <>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Ask Question
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Answer Display */}
      {answer && (
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              AI Answer
            </CardTitle>
            <CardDescription>
              Response based on video content analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-gradient-hero p-4 rounded-lg">
              <p className="leading-relaxed whitespace-pre-wrap">{answer}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Usage Tips */}
      <Card className="shadow-card bg-gradient-hero">
        <CardHeader>
          <CardTitle>💡 YouTube QA Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li>• Ensure the YouTube video is publicly accessible</li>
            <li>• Processing may take a few minutes for longer videos</li>
            <li>• Ask specific questions for more accurate answers</li>
            <li>• Try questions about key topics, timestamps, or specific details</li>
            <li>• The system works best with educational and informational content</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default YouTubeQA;