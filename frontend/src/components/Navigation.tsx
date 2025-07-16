import { useState, useEffect } from "react";
import { Home, LogIn, Search, Star, Film, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate, useLocation } from "react-router-dom";

export const Navigation = () => {
  const [userIsLoggedIn, setUserIsLoggedIn] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: Home, label: "Home", path: "/" },
    ...(userIsLoggedIn
      ? [{ icon: LogOut, label: "Logout", path: "/logout" }]
      : [{ icon: LogIn, label: "Login", path: "/login" }]),
  ];
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      setUserIsLoggedIn(true);
    } else {
      setUserIsLoggedIn(false);
    }
  }, []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => navigate("/")}
          >
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Film className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-foreground">
              StreamMovies
            </span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-6">
            {navItems.map(({ icon: Icon, label, path }) => (
              <Button
                key={path}
                variant="ghost"
                className={`text-foreground hover:text-primary transition-colors ${
                  location.pathname === path ? "text-primary" : ""
                }`}
                onClick={() => {
                  if (path === "/logout") {
                    localStorage.removeItem("token");
										console.log("logout");
										setUserIsLoggedIn(false);
                  } else {
                    navigate(path);
                  }
                }}
              >
                <Icon className="w-4 h-4 mr-2" />
                {label}
              </Button>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden text-foreground"
          >
            <Search className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </nav>
  );
};
