import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ProfileCardComponent } from "./components/profile-card/profile-card.component";
import { ProfileService } from './data/services/profile.service';
import { Profile } from './data/interfaces/profile.interface';
import { JsonPipe } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ProfileCardComponent, JsonPipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'frontend';
  profileService = inject(ProfileService)
  profiles: Profile[] = []

  constructor() {
    this.profileService.getProfiles()
      .subscribe(val => {
        this.profiles = val
      })
  }  
}
