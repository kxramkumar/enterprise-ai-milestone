import { useEffect, useState } from "react";
import "./App.css";

import { fetchAuthSession } from "aws-amplify/auth";
import { signOut } from "@aws-amplify/auth";
import { appConfig } from "./assets/app-exports.ts";

async function getAuthToken(): Promise<string | undefined> {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString();
  } catch (error) {
    console.error("Error getting auth token:", error);
    throw error;
  }
}

function App() {
  const [data, setData] = useState(null);
  useEffect(() => {
    console.log("mounted");
    getAuthToken()
      .then((token) => {
        if (token === undefined) {
          console.log("No token found");
          return;
        }
        console.log("URL: ", appConfig.backend_url);
        console.log("Token:", token);
        return fetch(appConfig.backend_url + "/protected", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      })
      .then((response) => response?.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error:", error));
  }, []);

  function handleSignOut() {
    signOut();
  }

  return (
    <>
      <h2>{data}</h2>
      <h3>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;by Kapil Disciples </h3>
      <div className="card">
        <button onClick={handleSignOut}>SignOut</button>
      </div>
    </>
  );
}

export default App;
