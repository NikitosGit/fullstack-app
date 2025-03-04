import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Profile } from '../interfaces/profile.interface';

@Injectable({
  providedIn: 'root',
})
export class ProfileService {
  http = inject(HttpClient);
  baseApiUrl = 'http://localhost:8000/';

  getProfiles() {
    return this.http.get<Profile[]>(`${this.baseApiUrl}items`);
  }

  getMe() {
    return this.http.get<Profile>(`${this.baseApiUrl}users/me`);
  }
}
