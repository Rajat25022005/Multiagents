import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, CheckCircle } from "lucide-react";
import { useState } from "react";

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} className="absolute top-2 right-2 text-gray-500 hover:text-gray-300 transition-colors">
      {copied ? <CheckCircle size={14} className="text-green-400" /> : <Copy size={14} />}
    </button>
  );
}

export default function ResultViewer({ content }) {
  if (!content) return null;
  return (
    <div className="prose-dark">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const code = String(children).replace(/\n$/, "");
            if (!inline && match) {
              return (
                <div className="relative">
                  <CopyButton text={code} />
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{ margin: 0, borderRadius: "0.5rem", fontSize: "0.8rem" }}
                    {...props}
                  >
                    {code}
                  </SyntaxHighlighter>
                </div>
              );
            }
            return <code className={className} {...props}>{children}</code>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
