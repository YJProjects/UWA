import {signUpUser} from "../backendAuth.ts";
import NavBar from "../../navbar/NavBar"
import "./SignUp.css"

export default function SignUp() {
    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        await signUpUser(email, password)

        console.log('Email:', email);
        console.log('Password:', password);
    }
    return (
        <div className = "signup">
            <form onSubmit={handleSubmit} className = 'signup-form'>
                <div className="signup-form-manual-input">
                    <div className="signup-form-input-text">Email</div>
                    <input className = "signup-input-box" type="text" name="email"></input><br></br>
                    <div className="signup-form-input-text">Password </div>
                    <input className = "signup-input-box" type="password" name="password" placeholder="*" /><br></br>
                    <input type="submit" value="Submit" />
                </div>
            </form>
        </div>
    )
}