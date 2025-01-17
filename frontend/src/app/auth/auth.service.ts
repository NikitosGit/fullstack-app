import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  http = inject(HttpClient)
  baseApiUrl = 'http://localhost:8000/auth/'
  login(payload: {username: string, password: string}) {
    const fd = new FormData()

    fd.append('username', payload.username)
    fd.append('password', payload.password)
    
     return this.http.post(
      `${this.baseApiUrl}token`, 
      fd
    )
  }
}
