import { BACKEND_URL } from "../../config";

interface SignUpRequest {
  email: string;
  password: string;
}

interface SignUpResponse {
  status : Number
  message : string
}

async function signUpUser(email: string, password: string): Promise<SignUpResponse> {
  const url = BACKEND_URL + "/auth/signup"
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    } satisfies SignUpRequest),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.error || "Signup failed");
  }

  const data = await response.json();

  console.log(data)
  return data;
}

export {
  signUpUser,
}