export type LoginCredentials = {
  username: string
  password: string
}

export type TokenPair = {
  access: string
  refresh: string
}

export type CurrentUser = {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: string
}
