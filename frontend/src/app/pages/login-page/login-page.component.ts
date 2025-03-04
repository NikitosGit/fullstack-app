import { Component, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { AuthService } from '../../auth/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.scss',
})
export class LoginPageComponent {
  authService = inject(AuthService);
  router = inject(Router);

  form = new FormGroup({
    username: new FormControl<string>('', Validators.required),
    password: new FormControl<string>('', Validators.required),
  });

  onSubmit() {
    if (this.form.valid) {
      console.log(this.form.value);

      //ts-ignore - заглушиить ошибку, без нее будет ругаться на this.form.value
      //@ts-ignore
      this.authService.login(this.form.value).subscribe((res) => {
        this.router.navigate(['']);
        console.log(res);
      });
    }
  }
}
