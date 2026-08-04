import { useNavigate, Link } from "react-router-dom";
import "./Login.css";
import { useEffect } from "react";
import { getFirebaseAuth } from "../../../firebase/firebaseAuth";
import { onAuthStateChanged, type Auth } from 'firebase/auth';
import { signInWithEmailAndPassword, setPersistence, browserLocalPersistence } from "firebase/auth";

export default function Login() {

    const navigate = useNavigate();
    const firebaseAuth : Auth = getFirebaseAuth();

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(firebaseAuth, (user) => {
            if (user) {
                navigate("/dashboard", { replace: true });
            }
        });

        return unsubscribe;
    }, [firebaseAuth, navigate]);


    async function loginUser(email: string, password: string): Promise<void> {
       
        await setPersistence(firebaseAuth, browserLocalPersistence)
        await signInWithEmailAndPassword(firebaseAuth, email, password)
    }
    
    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        try {
            await loginUser(email, password);
        } catch {
            alert("Invalid username or password")
        }
    }

    return (
        <main className="login-page">
            <section className="login-card" aria-labelledby="login-title">
                <header className="login-header">
                    <div className="login-brand" aria-label="UWA">
                        <span className="login-brand-mark" aria-hidden="true">U</span>
                        <span>UWA</span>
                    </div>

                    <h1 id="login-title">Welcome back</h1>
                    <p>
                        Sign in to get the alerts as soon as your class opens.
                    </p>
                </header>

                <form className="login-form" onSubmit={handleSubmit}>
                    <label className="login-field">
                        <span>Email</span>
                        <input
                            type="email"
                            name="email"
                            placeholder="you@example.com"
                            autoComplete="email"
                            required
                        />
                    </label>

                    <label className="login-field">
                        <span>Password</span>
                        <input
                            type="password"
                            name="password"
                            placeholder="Enter your password"
                            autoComplete="current-password"
                            required
                        />
                    </label>

                    <button className="login-button" type="submit">
                        Sign in
                    </button>
                </form>

                <div className="login-divider" aria-hidden="true">
                    <span>New to UWA?</span>
                </div>

                <Link className="signup-button" to="/signup">
                    Create an account
                </Link>
            </section>

            <p className="login-footer">Simple work. Clear progress.</p>
        </main>
    );
}
