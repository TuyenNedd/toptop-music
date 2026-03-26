---
stepsCompleted:
  [
    "step-01-init",
    "step-02-discovery",
    "step-02b-vision",
    "step-02c-executive-summary",
    "step-03-success",
    "step-04-journeys",
    "step-05-domain",
    "step-06-innovation",
    "step-07-project-type",
    "step-08-scoping",
    "step-09-functional",
    "step-10-nonfunctional",
    "step-11-polish",
    "step-12-complete",
    "step-e-01-discovery",
    "step-e-02-review",
    "step-e-03-edit",
  ]
inputDocuments:
  - "_bmad-output/planning-artifacts/research/technical-tiktok-api-research-2026-03-25.md"
  - "clean_plan.md"
workflowType: "prd"
documentCounts:
  briefs: 0
  research: 1
  brainstorming: 0
  projectDocs: 0
classification:
  projectType: "web_app"
  domain: "entertainment_media"
  complexity: "medium"
  projectContext: "greenfield"
lastEdited: "2026-03-26"
editHistory:
  - date: "2026-03-26"
    changes: "Post-validation fixes: FR implementation leakage cleanup (6 FRs rewritten), FR merges (FR5+FR6, FR45+FR46), added Journey 6 (playback failure), added FRs for email notification and playback resilience (FR45-FR49), NFR implementation leakage cleanup, scope consolidation, FR re-numbering (49 total FRs), MVP scope updated"
---

# Product Requirements Document - toptop-music

**Author:** Nedd
**Date:** 2026-03-26

## Executive Summary

toptop-music is a private, invite-only web application that extracts and streams audio from TikTok's trending sounds catalog, targeting the Vietnam market. The product strips away TikTok's video-centric experience to deliver a pure music listening interface — trending discovery, search, and continuous playback without visual distractions.

The application serves a small trusted group (friends and family) who appreciate TikTok's high-quality audio encoding but want a dedicated listening experience. Built on FastAPI (Python) with a Next.js frontend, the system scrapes TikTok's trending data via the unofficial TikTok-Api library, caches audio files locally, and streams them through a secured backend proxy. The architecture is designed production-grade from day one: JWT authentication, role-based access control, signed streaming URLs, structured audit logging, and multi-layer rate limiting.

This is also a deliberate learning project — the builder aims to experience full-stack system integration end-to-end: backend API design, web scraping with anti-bot handling, caching strategies, frontend audio player architecture, security implementation, CI/CD pipelines, and Docker-based deployment. The dual goal is a functional product for personal use and deep technical skill development.

### What Makes This Special

TikTok curates some of the highest-quality trending audio in Vietnam — V-pop, remixes, international hits, and original creator sounds — but locks the listening experience inside a short-form video feed. toptop-music unlocks that audio catalog as a standalone music player. Users open the app, see what's trending in Vietnam right now, hit play, and listen continuously. No video buffering, no algorithmic feed interruptions, no ads. Search lets users find specific sounds beyond the trending list. The experience is closer to Spotify than TikTok, but the content source is TikTok's uniquely curated sound library.

The web-first approach with a clear path to mobile (via Capacitor) means the product starts accessible on any device with a browser, then scales to native apps when ready — same codebase, no rewrite.

## Project Classification

- **Project Type:** Web Application (audio streaming player)
- **Domain:** Entertainment / Media
- **Complexity:** Medium — unofficial API dependency with anti-bot measures, multi-layer caching, production security requirements
- **Project Context:** Greenfield — new product, no existing codebase
- **Target Market:** Vietnam (VN trending sounds, VN IP proxy required)
- **Access Model:** Private, invite-only (admin generates invite codes)

## Success Criteria

### User Success

- Audio streaming starts within 2 seconds for cached sounds, under 5 seconds for on-demand
- Continuous playback without interruption — zero buffering gaps during normal network conditions
- Audio quality matches TikTok's original encoding (no re-encoding or quality loss)
- Trending list refreshed every 30-60 minutes with accurate Vietnam trending data
- Search returns results within 1 second for title/artist queries
- Users can create and manage personal playlists
- Users can mark sounds as favorites for quick access
- Seamless play queue — users can queue multiple sounds and listen continuously

### Business Success

- 5-15 active users (friends and family) using the app weekly within first month
- Builder (Nedd) and close circle actively use it as primary TikTok music listening tool
- Full-stack learning objectives achieved: backend API, scraping, caching, frontend audio player, security, CI/CD, Docker deployment, monitoring
- System runs self-sufficiently with minimal manual intervention (automated trending fetcher, cache management, token rotation alerts)

### Technical Success

- CI/CD pipeline fully automated via GitHub Actions (lint → test → build → deploy)
- 80%+ backend test coverage (unit + integration)
- Zero-downtime deployment via Docker Compose rolling updates
- Audio cache hit ratio > 70% for trending sounds (pre-cached)
- API response time p95 < 200ms for metadata endpoints
- Structured logging with audit trail for all security-sensitive actions
- Multi-layer rate limiting operational (Nginx + per-user + per-endpoint)
- TikTok-Api scraper resilient: automatic retry, fallback to yt-dlp, circuit breaker on sustained failures
- HTTPS everywhere, JWT auth, signed streaming URLs, OWASP API Top 10 coverage
- Monitoring dashboards with alerting on critical failures

### Measurable Outcomes

| Metric                         | Target   | Measurement                  |
| ------------------------------ | -------- | ---------------------------- |
| Time to first play (cached)    | < 2s     | Frontend performance logging |
| Time to first play (on-demand) | < 5s     | Backend streaming latency    |
| Trending data freshness        | < 60 min | Fetcher cycle monitoring     |
| API uptime                     | 99%+     | Health check monitoring      |
| Test coverage                  | 80%+     | pytest-cov reports in CI     |
| Cache hit ratio (trending)     | > 70%    | Redis + filesystem metrics   |
| Active users (monthly)         | 5-15     | Audit log unique user count  |

## Product Scope

### MVP - Minimum Viable Product

- User authentication (invite-only registration + open sign-up with admin approval)
- Trending sounds list (Vietnam region, auto-refreshed)
- Audio streaming with persistent player (play/pause, skip, volume, seek)
- Sound search by title/artist
- Favorites (mark/unmark sounds as favorite, favorites list view)
- Basic playlists (create, add/remove sounds, play playlist)
- Admin dashboard (user management, invite code generation, system health)
- Audio caching (pre-cache trending, on-demand cache for others)
- Secure audio access with time-limited authorization
- Email notification on account approval/rejection
- Playback resilience (auto-retry, graceful skip, cached-only fallback)
- Containerized deployment with reverse proxy + SSL
- CI/CD pipeline
- Structured logging + basic monitoring

### Growth Features (Post-MVP)

- Play history and "recently played" section
- Playlist sharing between users
- Sound recommendations based on listening history
- Audio visualizer (waveform/spectrum)
- Offline mode (PWA service worker caching)
- Push notifications for new trending sounds
- Advanced admin analytics (listening stats, popular sounds, user activity)
- Elasticsearch for improved Vietnamese full-text search

### Vision (Future)

- Mobile app via Capacitor (iOS + Android)
- Background audio playback on mobile
- Social features (shared playlists, listening activity feed)
- Multiple region support (not just VN)
- Paid API fallback integration (TikAPI/EnsembleData) for reliability
- Auto-discovery of sounds from specific TikTok creators/hashtags

## User Journeys

### Journey 1: Minh — The Daily Listener (Member, Happy Path)

Minh, 24 tuổi, là bạn thân của Nedd. Anh ấy nghiện TikTok nhưng hay phàn nàn: "Mình chỉ muốn nghe nhạc thôi, không muốn xem video liên tục." Mỗi khi nghe được bài hay trên TikTok, Minh phải Shazam rồi tìm trên Spotify — nhưng nhiều bài remix/original của creators VN không có trên Spotify.

Nedd gửi cho Minh một invite link. Minh mở browser, nhập invite code, tạo account trong 30 giây. Trang chủ hiện ra trending list — top 50 sounds đang hot trên TikTok VN ngay lúc này. Minh bấm play bài đầu tiên, âm thanh phát ra ngay lập tức, chất lượng y hệt như nghe trên TikTok. Player bar cố định ở dưới màn hình, Minh scroll qua list, bấm thêm vài bài vào queue.

Minh tìm thấy bài remix mà hôm qua nghe trên TikTok — bấm heart để thêm vào favorites. Sau đó tạo playlist "Chill Đêm" và kéo vài bài vào. Từ giờ mỗi tối, Minh mở toptop-music, bấm play playlist "Chill Đêm" và nghe liên tục không gián đoạn. Không video, không ads, không scroll.

**Capabilities revealed:** Registration via invite code, trending list display, instant audio playback, play queue, favorites, playlist CRUD, persistent player, search.

### Journey 2: Minh — Can't Find a Sound (Member, Edge Case)

Minh nhớ bài nhạc nghe trên TikTok hôm qua nhưng không nhớ tên. Anh ấy thử search "remix chill" — kết quả trả về vài bài nhưng không đúng. Minh thử search bằng từ khóa khác "lofi vn" — vẫn không tìm thấy. Bài đó có thể chưa được crawl vì không nằm trong trending.

Minh thấy thông báo nhẹ: "Không tìm thấy? Trending list cập nhật mỗi 30-60 phút. Bài mới có thể xuất hiện sau." Minh quay lại trending list, nghe bài khác. Ngày hôm sau, bài đó xuất hiện trong trending — Minh tìm thấy và thêm vào playlist ngay.

**Capabilities revealed:** Search with no results handling, graceful messaging, trending refresh cycle awareness, sound discovery over time.

### Journey 3: Nedd — The Admin (Admin User)

Nedd mở admin dashboard mỗi sáng. Dashboard hiện: 12 active users tuần này, 847 sounds đã cache, disk usage 3.2GB/10GB, TikTok-Api status: healthy, last trending fetch: 15 phút trước.

Em gái Nedd muốn dùng app. Nedd vào admin panel, generate invite code với expiry 7 ngày, copy và gửi qua Zalo. Nedd thấy có 1 pending user trong approval queue — đồng nghiệp cũ tự đăng ký. Nedd bấm Approve, user được kích hoạt.

Nedd check audit log: 3 failed login attempts từ IP lạ đêm qua — kiểm tra thấy là bot scan, rate limiter đã block. Không cần action.

Nedd nhận alert trên Grafana: TikTok-Api failure rate tăng lên 40% trong 2 giờ qua. Nedd check logs, thấy `EmptyResponseException` liên tục — TikTok đang block. Nedd rotate ms_token mới, restart scraper session. Failure rate giảm về 0%. Trending data tiếp tục cập nhật bình thường.

**Capabilities revealed:** Admin dashboard (user stats, system health, cache stats), invite code generation, pending user approval, audit log viewing, alert monitoring, ms_token management, scraper session control.

### Journey 4: Lan — First-Time Invited User (New User, Invite Path)

Lan, chị gái của Nedd, nhận link invite qua Zalo. Chị không rành công nghệ lắm. Mở link trên Safari iPhone, thấy trang register đơn giản: username, email, password, invite code (đã tự điền từ link). Bấm "Tạo tài khoản" — xong, account active ngay.

Trang chủ hiện trending list với cover art đẹp. Lan bấm bài đầu tiên — nhạc phát ngay. Chị thấy icon heart, bấm thử — "Đã thêm vào yêu thích." Lan không cần hướng dẫn gì thêm, UI đủ trực quan. Chị nghe nhạc 20 phút rồi tắt browser. Hôm sau mở lại, favorites vẫn còn, playlist vẫn đó.

**Capabilities revealed:** Invite link with pre-filled code, simple registration flow, instant activation with invite code, intuitive UI for non-tech users, mobile browser compatibility, persistent user data across sessions, responsive design.

### Journey 5: Hùng — Self-Registered User (New User, Approval Path)

Hùng, đồng nghiệp cũ của Nedd, nghe Minh kể về toptop-music. Hùng không có invite code nhưng tìm thấy link app. Mở trang register, thấy 2 option: "Có invite code" và "Đăng ký chờ duyệt." Hùng chọn đăng ký chờ duyệt, điền username, email, password. Bấm submit.

Màn hình hiện: "Tài khoản đã tạo thành công. Đang chờ admin duyệt — bạn sẽ nhận email khi tài khoản được kích hoạt." Hùng thử login — thấy thông báo: "Tài khoản chưa được kích hoạt. Vui lòng chờ admin duyệt."

Nedd nhận notification trên admin dashboard: "1 pending user: Hùng (hung@email.com)." Nedd nhận ra đây là đồng nghiệp cũ, bấm Approve. Hùng nhận email: "Tài khoản đã được kích hoạt." Login lại — vào app bình thường, thấy trending list, bắt đầu nghe nhạc.

**Capabilities revealed:** Dual registration paths (invite code vs open sign-up), pending account state, admin approval workflow, email notification on approval, pending user list in admin dashboard, login blocked for pending accounts.

### Journey 6: Minh — Playback Fails Mid-Listen (Member, Error Path)

Minh đang nghe playlist "Chill Đêm" được 15 phút. Bài thứ 4 đang phát, đột nhiên âm thanh dừng. Player hiện icon loading spinner 2 giây, rồi chuyển sang thông báo nhẹ: "Đang thử lại..."

Hệ thống tự động thử lại từ nguồn khác. Sau 3 giây, nhạc tiếp tục — Minh hầu như không nhận ra gián đoạn. Player hiện nhẹ: "Đã khôi phục playback ✓" rồi fade out.

Trường hợp xấu hơn: cả nguồn backup cũng fail. Player hiện: "Bài này tạm thời không khả dụng" và tự động skip sang bài tiếp theo trong queue. Minh thấy bài bị skip có icon ⚠️ nhỏ. Nhạc tiếp tục chảy — trải nghiệm không bị phá vỡ hoàn toàn.

Trường hợp xấu nhất: TikTok block hoàn toàn, nhiều bài liên tiếp fail. Sau 3 bài fail liên tục, player hiện toast: "Đang gặp sự cố kết nối nguồn nhạc. Các bài đã cache vẫn phát được bình thường." Player tự động filter queue chỉ còn cached sounds và tiếp tục phát.

**Capabilities revealed:** Automatic retry from alternative source, graceful skip on failure, cached-only fallback mode, non-disruptive error messaging, continuous playback resilience.

### Journey Requirements Summary

| Capability Area                                              | Journeys   | Priority |
| ------------------------------------------------------------ | ---------- | -------- |
| Dual registration (invite code + open sign-up with approval) | J1, J4, J5 | MVP      |
| Pending account state + admin approval workflow              | J5         | MVP      |
| Email notification on account approval                       | J5         | MVP      |
| Trending list (VN, auto-refresh)                             | J1, J2     | MVP      |
| Audio streaming (instant, quality)                           | J1, J4     | MVP      |
| Persistent player (queue, controls)                          | J1         | MVP      |
| Search (title/artist)                                        | J1, J2     | MVP      |
| Favorites                                                    | J1, J4     | MVP      |
| Playlists (CRUD, play)                                       | J1         | MVP      |
| No-results handling                                          | J2         | MVP      |
| Admin dashboard (stats, health, cache)                       | J3         | MVP      |
| Invite code management                                       | J3, J4     | MVP      |
| Pending users list + approve/reject                          | J3, J5     | MVP      |
| Audit logs                                                   | J3         | MVP      |
| System health monitoring                                     | J3         | MVP      |
| ms_token / scraper management                                | J3         | MVP      |
| Responsive mobile browser UI                                 | J4         | MVP      |
| Playback auto-retry from alternative source                  | J6         | MVP      |
| Graceful skip on unavailable sound                           | J6         | MVP      |
| Cached-only fallback mode                                    | J6         | MVP      |
| Non-disruptive playback error messaging                      | J6         | MVP      |
| Alert notifications (admin)                                  | J3         | Growth   |

## Domain-Specific Requirements

### Legal & Terms of Service

- TikTok Terms of Service prohibit automated scraping — this product operates in a non-official capacity
- All usage is private, non-commercial, invite-only — minimizes legal exposure
- No content redistribution or public sharing of audio files
- No user-facing download functionality — stream-only to reduce copyright risk
- Audio files cached server-side for performance only, not for distribution

### Content & Copyright

- Audio content sourced from TikTok's public trending feed — no user-authenticated or private content accessed
- Many TikTok sounds are original creator content (not licensed music) — lower copyright risk
- No metadata modification or content re-packaging
- If a sound is removed from TikTok, cached version should be flagged and eventually purged

### Unofficial API Dependency

- TikTok-Api is community-maintained, not officially supported by TikTok
- TikTok may change internal APIs at any time, breaking the scraper
- Fallback strategy required: yt-dlp as secondary audio source, paid API (TikAPI/EnsembleData) as tertiary
- ms_token expiration requires manual intervention — monitoring and alerting essential
- Anti-bot measures may escalate — proxy rotation and session management must be resilient

### Risk Mitigations

| Risk                              | Mitigation                                                  |
| --------------------------------- | ----------------------------------------------------------- |
| TikTok legal action               | Private-only, non-commercial, no public access, no download |
| Scraper permanently blocked       | Paid API fallback, yt-dlp backup                            |
| Copyright claim on specific sound | Remove from cache on detection, no redistribution           |
| ms_token expiration               | Multiple tokens, rotation mechanism, admin alerts           |

## Web Application Specific Requirements

### Project-Type Overview

toptop-music is a Single Page Application (SPA) with server-side rendering via Next.js App Router. The primary interaction model is a music player with list browsing — minimal page transitions, persistent audio player across all views.

### Browser & Device Support

| Browser                   | Minimum Version | Priority  |
| ------------------------- | --------------- | --------- |
| Chrome (Desktop + Mobile) | 90+             | Primary   |
| Safari (Desktop + iOS)    | 15+             | Primary   |
| Firefox                   | 90+             | Secondary |
| Samsung Internet          | 15+             | Secondary |
| Edge                      | 90+             | Low       |

- Mobile-first responsive design — majority of users will access via phone browser
- Minimum viewport: 320px width (iPhone SE)
- Target viewports: 375px (phone), 768px (tablet), 1024px+ (desktop)
- Touch-optimized controls for player (large tap targets, swipe gestures for queue)

### Performance Targets

| Metric                          | Target      | Context                             |
| ------------------------------- | ----------- | ----------------------------------- |
| First Contentful Paint (FCP)    | < 1.5s      | SSR trending list                   |
| Largest Contentful Paint (LCP)  | < 2.5s      | Cover art images loaded             |
| Time to Interactive (TTI)       | < 3s        | Player controls responsive          |
| Cumulative Layout Shift (CLS)   | < 0.1       | Stable layout with fixed player bar |
| Audio start latency (cached)    | < 2s        | Pre-cached MP3 streaming            |
| Audio start latency (on-demand) | < 5s        | Download + stream                   |
| API response (metadata)         | p95 < 200ms | Redis-cached responses              |

### SEO Strategy

- SEO is not a priority — private, invite-only app not intended for public discovery
- `robots.txt` disallow all crawlers
- `noindex, nofollow` meta tags on all pages
- No sitemap generation needed

### Accessibility Considerations

- Keyboard navigation for player controls (play/pause, skip, volume)
- ARIA labels on all interactive elements (player buttons, sound cards, search)
- Focus management for modal dialogs (playlist creation, queue drawer)
- Color contrast ratio minimum 4.5:1 for text
- Screen reader support for trending list and search results
- Reduced motion support for users who prefer minimal animations

### Real-Time Considerations

- No WebSocket needed — trending data refreshes via polling (30-60 min server-side)
- Audio player state managed client-side via Zustand (no server sync needed)
- Playlist/favorites changes saved via REST API calls (optimistic UI updates)

### Architecture Context (for downstream reference, not requirements)

- Next.js App Router with React Server Components for trending list (SSR)
- Client Components for player, search input, interactive elements
- Image optimization via Next.js Image for cover art (lazy loading, responsive sizes)
- Service Worker for basic offline shell (PWA manifest for Add to Home Screen)
- BFF proxy pattern: Next.js rewrites to FastAPI backend (no CORS, hidden API)

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Experience MVP — deliver the core listening experience end-to-end (trending → play → favorites → playlists) with production-grade quality. Not a throwaway prototype — this is the real product from day one.

**Resource Requirements:** Solo developer (Nedd), 8 weeks estimated timeline, $15-57/month operating costs.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:** J1 (Daily Listener), J2 (Search Edge Case), J3 (Admin), J4 (Invite User), J5 (Self-Register User), J6 (Playback Failure)

**Refer to Product Scope section above for complete MVP feature list.**

### Post-MVP Features

**Refer to Product Scope section above for Growth and Vision phase features.**

### Risk Mitigation Strategy

**Technical Risks:** TikTok-Api breakage mitigated by yt-dlp fallback + paid API tertiary option. Playwright memory managed by limiting to 1-2 sessions with proper cleanup.

**Market Risks:** Minimal — private app for known users. No market validation needed. Success = personal use satisfaction.

**Resource Risks:** Solo dev — if timeline extends, MVP scope can be reduced by deferring playlists to Phase 2 while keeping trending + play + favorites + search as absolute minimum.

## Functional Requirements

### User Registration & Authentication

- FR1: Visitors can register using an invite code for instant account activation
- FR2: Visitors can register without an invite code, creating a pending account awaiting admin approval
- FR3: Registered users can log in with username/email and password
- FR4: Authenticated users can log out from any device
- FR5: The system maintains authenticated sessions that renew automatically without requiring re-login

### Sound Discovery & Browsing

- FR6: Members can view a paginated list of trending sounds from TikTok Vietnam
- FR7: Members can see sound metadata (title, artist, cover art, duration, usage count, trend rank)
- FR8: Members can search sounds by title or artist name
- FR9: The system displays an informative message explaining search limitations and suggesting alternatives when search returns no results
- FR10: Members can view sound details including trending rank changes over time and days on trending list

### Audio Playback

- FR11: Members can play any sound from the trending list, search results, favorites, or playlists
- FR12: Members can pause, resume, skip to next, and go to previous sound
- FR13: Members can adjust playback volume
- FR14: Members can seek to any position within a playing sound
- FR15: Members can add sounds to a play queue
- FR16: Members can view and manage the current play queue
- FR17: The player persists across page navigation without interrupting playback

### Favorites

- FR18: Members can mark any sound as a favorite
- FR19: Members can remove a sound from favorites
- FR20: Members can view their complete favorites list
- FR21: Members can play all favorites as a continuous playlist

### Playlists

- FR22: Members can create named playlists
- FR23: Members can add sounds to a playlist
- FR24: Members can remove sounds from a playlist
- FR25: Members can rename a playlist
- FR26: Members can delete a playlist
- FR27: Members can view all their playlists
- FR28: Members can play an entire playlist continuously

### Administration

- FR29: Admins can view a dashboard with system health, user stats, cache stats, and scraper status
- FR30: Admins can generate invite codes with configurable expiration
- FR31: Admins can view and approve or reject pending user registrations
- FR32: Admins can activate or deactivate existing user accounts
- FR33: Admins can view audit logs filtered by event type, user, or date range
- FR34: Admins can view and manage TikTok-Api scraper status (session health, last fetch time)
- FR35: Admins can trigger manual trending data refresh

### Data Collection & Caching

- FR36: The system can automatically fetch trending sounds from TikTok Vietnam at configurable intervals
- FR37: The system can extract and store sound metadata including audio URLs from TikTok data
- FR38: The system can pre-download and cache audio files for top trending sounds
- FR39: The system can download and cache audio on-demand when a user plays an uncached sound
- FR40: The system can manage cache storage with automatic eviction when disk limits are reached
- FR41: The system can retrieve audio from alternative sources when primary audio URLs are unavailable or expired

### Audio Streaming

- FR42: The system supports audio seeking to any position during streaming playback of cached files
- FR43: The system can proxy-stream uncached audio from TikTok sources
- FR44: The system restricts audio access to authenticated users with time-limited, user-specific authorization that rejects expired or unauthorized requests

### Notifications

- FR45: The system sends email notifications to users when their pending account is approved or rejected by an admin

### Playback Resilience

- FR46: The system automatically retries audio playback from alternative sources when primary playback fails
- FR47: The system skips to the next queued sound when a sound is temporarily unavailable after retry attempts
- FR48: The system can filter playback to cached-only sounds when external audio sources are unreachable
- FR49: The system displays non-disruptive status messages during playback recovery without interrupting the listening experience

## Non-Functional Requirements

### Performance

- Cached audio playback starts within 2 seconds of user action
- On-demand audio playback starts within 5 seconds
- API metadata responses complete within 200ms at p95
- Search results return within 1 second
- Trending list page renders (FCP) within 1.5 seconds via SSR
- System supports 15 concurrent users without performance degradation

### Security

- All data transmitted over HTTPS (TLS 1.2+)
- Passwords hashed with a strong adaptive hashing algorithm (minimum work factor equivalent to bcrypt 12 rounds)
- JWT access tokens expire within 30 minutes
- Refresh tokens stored in httpOnly secure cookies
- All API endpoints require authentication except registration and login
- Audio streaming URLs are signed with a cryptographic hash and expire within 2 hours
- Failed login attempts trigger progressive lockout (5 attempts, 15 min cooldown)
- Multi-layer rate limiting: global (reverse proxy), per-user, per-endpoint
- All security-sensitive actions logged to audit trail
- OWASP API Security Top 10 mitigations implemented
- Security headers enforced (HSTS, CSP, X-Content-Type-Options, X-Frame-Options)
- CORS restricted to application domain only

### Reliability

- System uptime target: 99%+ (allows approximately 7 hours downtime per month for maintenance)
- TikTok-Api failures handled gracefully with cached data fallback
- Audio cache serves content even when TikTok is unreachable
- Database connection pool with automatic retry on transient failures
- Circuit breaker on TikTok-Api: stops requests after consecutive failures, auto-recovers

### Scalability

- Initial capacity: 15 concurrent users on single 4GB VPS
- Audio cache supports up to 10GB of stored sounds
- Database handles up to 10,000 sound records without index optimization
- Architecture supports vertical scaling (upgrade VPS) as first scaling step
- Modular monolith design allows future extraction to microservices if needed

### Maintainability

- 80%+ backend test coverage (unit + integration)
- Automated CI/CD pipeline (lint, test, build, deploy)
- Zero-downtime deployment via container orchestration rolling updates
- Structured JSON logging with correlation IDs for debugging
- Database migrations managed with versioned, reversible migration tooling
- All configuration via environment variables (no hardcoded secrets)
