import {signUpUser} from "../backendAuth.ts";
import NavBar from "../../navbar/NavBar"
import "./SignUp.css"
import { useState } from "react"

export default function SignUp() {
    const [password, setPassword] = useState('');
    const [passwordRules, setPasswordRules] = useState({
        length: false,
        number: false,
        capital: false
    });

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const firstName = formData.get('firstName') as string;
        const lastName = formData.get('lastName') as string;
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        await signUpUser(firstName, lastName, email, password)
    }

    function validatePassword(event: React.ChangeEvent<HTMLInputElement>) {
        /*
         Rules:
         - 1) Password length must be of 8 characters
         - 2) Password must contain one number
         - 3) Password must have a capital letter
        */
        const pwd = event.target.value;
        setPassword(pwd);

        setPasswordRules({
            length: pwd.length >= 8,
            number: /\d/.test(pwd),
            capital: /[A-Z]/.test(pwd)
        });
    }

    return (
        <div className = "signup">
            <form onSubmit={handleSubmit} className = 'signup-form'>
                <h1>Create Account</h1>
                <div className="signup-form-manual-input">
                    <div>
                        <div className="signup-form-input-text">First Name</div>
                        <input className = "signup-input-box" type="text" name="firstName" placeholder="Enter your first name" required></input>
                    </div>

                    <div>
                        <div className="signup-form-input-text">Last Name</div>
                        <input className = "signup-input-box" type="text" name="lastName" placeholder="Enter your last name" required></input>
                    </div>

                    <div>
                        <div className="signup-form-input-text">Email</div>
                        <input className = "signup-input-box" type="email" name="email" placeholder="Enter your email address" required></input>
                    </div>

                    <div>
                        <div className="signup-form-input-text">Password</div>
                        <input className = "signup-input-box" type="password" name="password" placeholder="Create a password" onChange={validatePassword} required />

                        <div className="signup-form-password-rules">
                            <div className={`rule ${passwordRules.length ? 'complete' : ''}`}>
                                Password length must be at least 8 characters
                            </div>
                            <div className={`rule ${passwordRules.number ? 'complete' : ''}`}>
                                Password must contain a number
                            </div>
                            <div className={`rule ${passwordRules.capital ? 'complete' : ''}`}>
                                Password must contain a capital letter
                            </div>
                        </div>
                    </div>

                    <input type="submit" value="Sign Up" />
                </div>
            </form>
        </div>
    )
}